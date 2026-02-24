from scripts.controller.stages import Stage


class TestFlow:
    def __init__(self, controller):
        self.ctrl = controller
        self.model = controller.model
        self.calc = controller.calc_data
        
    def search_hod(self):
        self.model.alarm_tag = ''
        self.model.flag_alarm = False
        self.model.flag_search_hod = True
        
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('medium', hod)
        self.ctrl.transition_via_buffer(Stage.SEARCH_HOD, speed=speed)
        
    def test_move_cycle(self):
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('medium', hod)
        self.ctrl.transition_via_buffer(Stage.TEST_MOVE_CYCLE, speed=speed)
        
    def pumping(self):
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('fast', hod)
        self.ctrl.transition_via_buffer(Stage.PUMPING, speed=speed)
    
    def test_on_two_speed(self, ind: int):
        if ind == 1:
                speed = self.model.data_test.amort.speed_one
                self.model.data_test.speed_test = speed
                self.ctrl.transition_via_buffer(Stage.TEST_SPEED_ONE, speed=speed)

        elif ind == 2:
            speed = self.model.data_test.amort.speed_two
            self.model.data_test.speed_test = speed
            self.ctrl.transition_via_buffer(Stage.TEST_SPEED_TWO, speed=speed)

        if self.model.flag_repeat:
            self.model.flag_repeat = False
            self.model.fc_control(**{'tag': 'up', 'adr': 1})
    
    def test_lab_hand_speed(self):
        speed = self.model.data_test.speed_test
        self.ctrl.transition_via_buffer(Stage.TEST_LAB_HAND_SPEED, speed=speed)

        if self.model.flag_repeat:
            self.model.flag_repeat = False
            self.model.fc_control(**{'tag': 'up', 'adr': 1})
    
    def test_lab_cascade(self):
        self.count_cascade = 1
        self.max_cascade = len(self.model.data_test.speed_list)
        speed = self.model.data_test.speed_list[0]
        self.model.data_test.speed_test = speed            
        self.ctrl.transition_via_buffer(Stage.TEST_LAB_CASCADE, speed=speed)
        
        if self.model.flag_repeat:
            self.model.flag_repeat = False
            self.model.fc_control(**{'tag': 'up', 'adr': 1})
            
    def test_temper(self):
        speed = self.model.data_test.speed_test
        self.ctrl.transition_via_buffer(Stage.TEST_TEMPER, speed=speed)

        if self.model.flag_repeat:
            self.model.flag_repeat = False
            self.model.fc_control(**{'tag': 'up', 'adr': 1})
    
    def stop_gear_end_test(self):
        self.ctrl.transition_via_buffer(Stage.STOP_GEAR_END_TEST, extra_fc={'tag': 'stop', 'adr': 1})

    def stop_gear_min_pos(self):
        hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
        speed = self.calc.definition_speed_by_hod('medium', hod)
        self.ctrl.transition_via_buffer(Stage.STOP_GEAR_MIN_POS, speed=speed)
