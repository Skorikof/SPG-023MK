from scripts.controller.stages import Stage

from config import config
from scripts.logger import my_logger


class TraverseService:
    def __init__(self, controller):
        self.ctrl = controller
        self.model = controller.model
        self.logger = my_logger.get_logger(__name__)
    
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
                    self.ctrl.signals.control_msg.emit('yellow_btn')
                else:
                    self.ctrl.set_stage(Stage.INSTALL_AMORT)
                    self.set_trav_point = install_point
                    self.ctrl.steps.step_traverse_move_position(install_point)
            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self.ctrl.set_stage(Stage.START_POINT_AMORT)
                self.set_trav_point = start_point
                self.ctrl.steps.step_traverse_move_position(start_point)
            elif tag == 'stop_test':
                end_point = int((stock_point + hod / 2) - len_max - adapter)
                self.ctrl.set_stage(Stage.STOP_TEST)
                self.set_trav_point = end_point
                self.ctrl.steps.step_traverse_move_position(end_point)

        except Exception as e:
            self.logger.error(e)
    
    def traverse_move_out_alarm(self, pos):
        try:
            if pos == 'up':
                self.set_trav_point = 20
            elif pos == 'down':
                self.set_trav_point = 550
            self.ctrl.set_stage(Stage.ALARM_TRAVERSE)
            self.ctrl.steps.step_traverse_move_position(self.set_trav_point)

        except Exception as e:
            self.logger.error(e)