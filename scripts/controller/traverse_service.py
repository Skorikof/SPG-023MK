# -*- coding: utf-8 -*-
import time
from PySide6.QtCore import QObject, Signal

from .stages import Stage
from config import config
from scripts.logger import my_logger
from scripts.model import Model


class TraverseServiceSignals(QObject):
    set_stage = Signal(object)
    control_msg = Signal(str)


class TraverseService:
    # возврат к цели после проезда: траверса считается вставшей, если положение меняется
    # не больше SETTLE_DELTA мм за SETTLE_TIME с; не дождались за SETTLE_TIMEOUT с -
    # положение принимается как есть
    MAX_CORRECTIONS = 2
    SETTLE_DELTA = 0.1
    SETTLE_TIME = 0.5
    SETTLE_TIMEOUT = 5.0

    def __init__(self, model: Model):
        self.model = model
        self.logger = my_logger.get_logger(__name__)
        self.signals = TraverseServiceSignals()
        self.set_trav_point = 0
        self.flag_freq_1_step = False
        self.flag_freq_2_step = False
        self.flag_freq_stop = False
        # направление текущего перемещения: 'up' - координата траверсы уменьшается,
        # 'down' - растёт, None - траверса не запускалась (уже в точке)
        self.move_dir = None
        # после проезда цели: время начала ожидания остановки (None - не ждём),
        # последнее положение и с какого момента оно не меняется, число возвратов к цели
        self._settle_start = None
        self._settle_since = 0.0
        self._settle_pos = 0.0
        self._corrections = 0
        # положение принято без попадания в ±0.3 мм (возвраты исчерпаны) - этап завершён
        self._accepted = False

    def set_traverse_position(self, point):
        self.set_trav_point = point
    
    def traverse_install_point(self, tag):
        """Позционирование траверсы"""
        try:
            stock_point = config.const_traverse
            hod = self.model.data_test.amort.hod
            len_min = self.model.data_test.amort.min_length
            len_max = self.model.data_test.amort.max_length
            mid_point = (len_max - len_min) / 2
            adapter = self.model.data_test.amort.adapter_len
            if tag == 'install':
                self.set_trav_point = round((stock_point + hod / 2) - len_max - adapter, 1)
                if abs(abs(self.model.move_traverse) - abs(self.set_trav_point)) < 0.5:
                    # траверса уже в точке установки (повторное испытание того же амортизатора):
                    # ждём запуска так же, как после позиционирования, иначе жёлтая кнопка не работает
                    self.model.flag_test_launch = True
                    self.signals.control_msg.emit('yellow_btn')
                else:
                    self.signals.set_stage.emit(Stage.INSTALL_AMORT)
                    self._traverse_move_position()
            elif tag == 'start_test':
                self.set_trav_point = int(stock_point - len_max - adapter + mid_point)
                self.signals.set_stage.emit(Stage.START_POINT_AMORT)
                self._traverse_move_position()
            elif tag == 'stop_test':
                self.set_trav_point = int((stock_point + hod / 2) - len_max - adapter)
                self.signals.set_stage.emit(Stage.STOP_TEST)
                self._traverse_move_position()

        except Exception as e:
            self.logger.error(e)
    
    def traverse_move_out_alarm(self, pos):
        try:
            if pos == 'up':
                self.set_trav_point = 50
            elif pos == 'down':
                self.set_trav_point = 500
            self.signals.set_stage.emit(Stage.ALARM_TRAVERSE)
            self._traverse_move_position()

        except Exception as e:
            self.logger.error(e)
            
    def _traverse_move_position(self, correction: bool = False):
        """Непосредственно включение и перемещение траверсы (correction - возврат после проезда цели)"""
        try:
            self._settle_start = None
            self._accepted = False
            if not correction:
                self._corrections = 0
            val = abs(self.set_trav_point - self.model.move_traverse)
            self.move_dir = None
            if val > 0.3:
                if val <= 10:
                    freq = 5
                elif 10 < val < 20:
                    freq = 15
                else:
                    freq = 30
                    
                self.flag_freq_1_step = False
                self.flag_freq_2_step = False
                self.flag_freq_stop = False
                self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': freq})

                if self.model.move_traverse > self.set_trav_point:
                    tag = 'up'
                else:
                    tag = 'down'
                self.move_dir = tag
                self.model.fc_control(**{'tag': tag, 'adr': 2})

        except Exception as e:
            self.logger.error(e)

    def step_control_traverse_move(self) -> bool:
        """Функция отслеживания траверсы, при достижении точки останов"""
        try:
            if self._accepted:
                return True
            if self._settle_start is not None:
                return self._step_settle_after_overshoot()

            if 8 < abs(self.set_trav_point - self.model.move_traverse) <= 15:
                if not self.flag_freq_1_step:
                    self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': 15})
                    self.flag_freq_1_step = True

            if 2 < abs(self.set_trav_point - self.model.move_traverse) <= 8:
                if not self.flag_freq_2_step:
                    self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': 5})
                    self.flag_freq_2_step = True

            if abs(self.set_trav_point - self.model.move_traverse) <= 0.3:
                if not self.flag_freq_stop:
                    self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                    self.flag_freq_stop = True
                return True

            # Проехала цель, не попав в окно ±0.3 мм (задержка команды «стоп», рывок):
            # раньше стоп подавался только внутри окна, и траверса ехала дальше до концевика
            overshoot = ((self.move_dir == 'up' and self.model.move_traverse < self.set_trav_point - 0.3)
                         or (self.move_dir == 'down' and self.model.move_traverse > self.set_trav_point + 0.3))
            if overshoot:
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                self.flag_freq_stop = True
                self.logger.warning(f'Траверса проехала цель {self.set_trav_point} ({self.move_dir}): '
                                    f'положение {self.model.move_traverse}, стоп')
                self.move_dir = None
                self._settle_since = time.monotonic()
                self._settle_pos = self.model.move_traverse
                self._settle_start = self._settle_since

            return False

        except Exception as e:
            self.logger.error(e)

    def _step_settle_after_overshoot(self) -> bool:
        """
        После проезда цели: ждём, пока траверса встанет (положение не меняется
        SETTLE_TIME с), и возвращаем её к цели на малой скорости. Не больше
        MAX_CORRECTIONS возвратов - дальше принимаем положение как есть (WARNING),
        чтобы не раскачивать траверсу туда-обратно
        """
        try:
            now = time.monotonic()
            pos = self.model.move_traverse
            if abs(pos - self._settle_pos) > self.SETTLE_DELTA:
                self._settle_pos = pos
                self._settle_since = now
            stood = now - self._settle_since >= self.SETTLE_TIME
            timed_out = now - self._settle_start >= self.SETTLE_TIMEOUT
            if not (stood or timed_out):
                return False

            self._settle_start = None
            error = self.set_trav_point - pos
            if abs(error) <= 0.3:
                self.logger.info(f'Траверса после проезда цели в точке {self.set_trav_point}: положение {pos}')
                return True
            if self._corrections >= self.MAX_CORRECTIONS or timed_out:
                self.logger.warning(f'Траверса не вернулась в цель {self.set_trav_point}: положение {pos} '
                                    f'(отклонение {error:+.1f} мм, возвратов {self._corrections}'
                                    f'{", не встала за %.0f с" % self.SETTLE_TIMEOUT if timed_out else ""}), '
                                    f'положение принято')
                self._accepted = True
                return True

            self._corrections += 1
            self.logger.warning(f'Траверса: возврат к цели {self.set_trav_point} из {pos} '
                                f'(№{self._corrections}/{self.MAX_CORRECTIONS})')
            self._traverse_move_position(correction=True)
            return False

        except Exception as e:
            self.logger.error(e)
            self._settle_start = None
            self._accepted = True
            return True

    def step_traverse_referent_point(self):
        """Подъём траверсы до концевика для определения референтной точки"""
        try:
            self.signals.set_stage.emit(Stage.TRAVERSE_REFERENT)
            self.model.fc_control(**{'tag':'speed', 'adr':2, 'freq':30})
            self.model.fc_control(**{'tag': 'up', 'adr': 2})

        except Exception as e:
            self.logger.error(e)
    
    def flag_traverse_referent(self):
        try:
            if self.model.switch_dict.get('highest_position', False) is True:
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                
                self.model.init_timer_koef_force()

                return True
            return False

        except Exception as e:
            self.logger.error(e)
