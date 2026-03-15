# -*- coding: utf-8 -*-
from PySide6.QtCore import QObject, Signal

from .stages import Stage
from config import config
from scripts.logger import my_logger
from scripts.model import Model


class TraverseServiceSignals(QObject):
    set_stage = Signal(object)
    control_msg = Signal(str)


class TraverseService:
    def __init__(self, model: Model):
        self.model = model
        self.logger = my_logger.get_logger(__name__)
        self.signals = TraverseServiceSignals()
        self.set_trav_point = 0
        self.flag_freq_1_step = False
        self.flag_freq_2_step = False
        self.flag_freq_stop = False
        
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
            
    def _traverse_move_position(self):
        """Непосредственно включение и перемещение траверсы"""
        try:
            val = abs(self.set_trav_point - self.model.move_traverse)
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
                self.model.fc_control(**{'tag': tag, 'adr': 2})

        except Exception as e:
            self.logger.error(e)

    def step_control_traverse_move(self) -> bool:
        """Функция отслеживания траверсы, при достижении точки останов"""
        try:
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

            return False

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
    
    def flag_traverse_referent(self):
        try:
            if self.model.switch_dict.get('highest_position', False) is True:
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                
                self.model.init_timer_koef_force() # FIXME Тут происходит запуск обнудения датчика усилия

                return True
            return False

        except Exception as e:
            self.logger.error(e)
