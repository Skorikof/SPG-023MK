from PySide6.QtCore import QObject, Signal

from .stages import Stage
from config import config
from scripts.logger import my_logger


class TraverseServiceSignals(QObject):
    set_stage = Signal(object)
    control_msg = Signal(str)


class TraverseService:
    def __init__(self, model):
        self.model = model
        self.logger = my_logger.get_logger(__name__)
        self.signals = TraverseServiceSignals()
    
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
                install_point = round((stock_point + hod / 2) - len_max - adapter, 1)
                if abs(abs(self.model.move_traverse) - abs(install_point)) < 0.5:
                    self.signals.control_msg.emit('yellow_btn')
                else:
                    self.signals.set_stage.emit(Stage.INSTALL_AMORT)
                    self.set_trav_point = install_point
                    self._traverse_move_position(install_point)
            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self.signals.set_stage.emit(Stage.START_POINT_AMORT)
                self.set_trav_point = start_point
                self._traverse_move_position(start_point)
            elif tag == 'stop_test':
                end_point = int((stock_point + hod / 2) - len_max - adapter)
                self.signals.set_stage.emit(Stage.STOP_TEST)
                self.set_trav_point = end_point
                self._traverse_move_position(end_point)

        except Exception as e:
            self.logger.error(e)
    
    def traverse_move_out_alarm(self, pos):
        try:
            if pos == 'up':
                self.set_trav_point = 20
            elif pos == 'down':
                self.set_trav_point = 550
            self.signals.set_stage.emit(Stage.ALARM_TRAVERSE)
            self._traverse_move_position(self.set_trav_point)

        except Exception as e:
            self.logger.error(e)
            
    def _traverse_move_position(self, set_point):
        """Непосредственно включение и перемещение траверсы"""
        try:
            val = abs(set_point - self.model.move_traverse)
            if val > 0.3:
                if val <= 10:
                    freq = 5
                elif 10 < val < 20:
                    freq = 15
                else:
                    freq = 30
                    
                self.flag_freq_1_step = False
                self.flag_freq_2_step = False
                self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': freq})
                pos_trav = self.model.move_traverse

                if pos_trav > set_point:
                    tag = 'up'
                else:
                    tag = 'down'
                self.model.fc_control(**{'tag': tag, 'adr': 2})

        except Exception as e:
            self.logger.error(e)

    def step_control_traverse_move(self, point) -> bool:
        """Функция отслеживания траверсы, при достижении точки останов"""
        try:
            if 8 < abs(point - self.model.move_traverse) <= 15:
                if not self.flag_freq_1_step:
                    self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': 15})
                    self.flag_freq_1_step = True

            if 2 < abs(point - self.model.move_traverse) <= 8:
                if not self.flag_freq_2_step:
                    self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': 5})
                    self.flag_freq_2_step = True

            if abs(point - self.model.move_traverse) <= 0.3:
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                # print(f'Остановился -- {self.model.move_traverse}')
                return True

            return False

        except Exception as e:
            self.logger.error(e)

    def step_move_traverse_out_alarm(self, pos):
        try:
            tag = 'down'
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': 30})
            if pos == 'up':
                tag = 'down'
            elif pos == 'down':
                tag = 'up'
            self.model.fc_control(**{'tag': tag, 'adr': 2})

        except Exception as e:
            self.logger.error(e)
            
    def step_traverse_referent_point(self):
        """Подъём траверсы до концевика для определения референтной точки"""
        try:
            self.signals.set_stage.emit(Stage.TRAVERSE_REFERENT)
            self.model.fc_control(**{'tag':'speed', 'adr':2, 'freq':30})
            self.model.fc_control(**{'tag': 'up', 'adr': 2})

        except Exception as e:
            self.logger.error(e)
    
    def stage_traverse_referent(self):
        try:
            if self.model.switch_dict.get('highest_position', False) is True:
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                self.model.init_timer_koef_force()

                return True
            return False

        except Exception as e:
            self.logger.error(e)
