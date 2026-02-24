from PySide6.QtCore import QObject, Signal

from .stages import Stage
from scripts.data_calculation import CalcData


class TestFlowSignals(QObject):
    set_stage = Signal(object)
    set_next_stage = Signal(object)


class TestFlow:
    def __init__(self, model):
        self.signals = TestFlowSignals()
        self.model = model
        self.calc = CalcData()
        
    def transition_via_buffer(
        self,
        next_stage: Stage,
        *,
        speed=None,
        adr=1,
        force_cycle=True,
        extra_fc=None
    ):
        """
        Унифицированный переход через WAIT_BUFFER.
        Parameters
        ----------
        next_stage : Stage
            Куда перейти после buffer_on
        speed : int | None
            Если задан — отправим fc_control speed
        adr : int
            Адрес привода
        force_cycle : bool
            Нужно ли включать force_cycle
        extra_fc : dict | None
            Любая дополнительная команда fc_control
        """
        if force_cycle:
            self.model.write_bit_force_cycle(1)
        if speed is not None:
            self.model.fc_control(tag='speed', adr=adr, speed=speed)
        if extra_fc:
            self.model.fc_control(**extra_fc)

        self.signals.set_next_stage.emit(next_stage)
        self.signals.set_stage.emit(Stage.WAIT_BUFFER)
        
    def search_hod(self):
        self.model.alarm_tag = ''
        self.model.flag_alarm = False
        self.model.flag_search_hod = True
        
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('medium', hod)
        self.transition_via_buffer(Stage.SEARCH_HOD, speed=speed)
        
    def move_gear_set_pos(self):
        self.model.alarm_tag = ''
        self.model.flag_alarm = False
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('slow', hod)
        self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed})
        self.transition_via_buffer(Stage.POS_SET_GEAR, speed=speed)
        
    def test_move_cycle(self):
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('medium', hod)
        self.transition_via_buffer(Stage.TEST_MOVE_CYCLE, speed=speed)
        
    def pumping(self):
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('fast', hod)
        self.transition_via_buffer(Stage.PUMPING, speed=speed)
    
    def test_on_two_speed(self, ind: int):
        if ind == 1:
                speed = self.model.data_test.amort.speed_one
                self.model.data_test.speed_test = speed
                self.transition_via_buffer(Stage.TEST_SPEED_ONE, speed=speed)

        elif ind == 2:
            speed = self.model.data_test.amort.speed_two
            self.model.data_test.speed_test = speed
            self.transition_via_buffer(Stage.TEST_SPEED_TWO, speed=speed)

        if self.model.flag_repeat:
            self.model.flag_repeat = False
            self.model.fc_control(**{'tag': 'up', 'adr': 1})
    
    def test_lab_hand_speed(self):
        speed = self.model.data_test.speed_test
        self.transition_via_buffer(Stage.TEST_LAB_HAND_SPEED, speed=speed)

        if self.model.flag_repeat:
            self.model.flag_repeat = False
            self.model.fc_control(**{'tag': 'up', 'adr': 1})
    
    def test_lab_cascade(self):
        self.count_cascade = 1
        self.max_cascade = len(self.model.data_test.speed_list)
        speed = self.model.data_test.speed_list[0]
        self.model.data_test.speed_test = speed            
        self.transition_via_buffer(Stage.TEST_LAB_CASCADE, speed=speed)
        
        if self.model.flag_repeat:
            self.model.flag_repeat = False
            self.model.fc_control(**{'tag': 'up', 'adr': 1})
            
    def test_temper(self):
        speed = self.model.data_test.speed_test
        self.transition_via_buffer(Stage.TEST_TEMPER, speed=speed)

        if self.model.flag_repeat:
            self.model.flag_repeat = False
            self.model.fc_control(**{'tag': 'up', 'adr': 1})
    
    def stop_gear_end_test(self):
        self.transition_via_buffer(Stage.STOP_GEAR_END_TEST, extra_fc={'tag': 'stop', 'adr': 1})

    def stop_gear_min_pos(self):
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('medium', hod)
        self.transition_via_buffer(Stage.STOP_GEAR_MIN_POS, speed=speed)
