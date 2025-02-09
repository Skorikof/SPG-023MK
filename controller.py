# -*- coding: utf-8 -*-
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from logger import my_logger
from my_obj.data_calculation import CalcData
from my_obj.steps_logic import Steps


class ControlSignals(QObject):
    control_msg = pyqtSignal(str)
    traverse_referent_msg = pyqtSignal()
    wait_yellow_btn = pyqtSignal()
    conv_win_test = pyqtSignal()
    lab_win_test = pyqtSignal()
    lab_test_stop = pyqtSignal()
    lab_save_result = pyqtSignal(str)
    cancel_test = pyqtSignal()
    end_test = pyqtSignal()
    search_hod_msg = pyqtSignal()
    reset_ui = pyqtSignal()


class Controller:
    def __init__(self, model):
        try:
            self.logger = my_logger.get_logger(__name__)
            self.signals = ControlSignals()
            self.model = model
            self.steps = Steps(model)
            self.calc_data = CalcData()

            self.timer_process = None
            self.flag_alarm_traverse = True
            self.count_cycle = 0
            self.set_trav_point = 0
            self.cascade = 1
            self.max_cascade = 0
            self.flag_repeat = False

            self._init_signals()
            self._init_timer_test()

            # self.time_start_wait = None
            # self.time_all_wait = None
            # self.time_tag_wait = None
            # self.time_lost_control = time.monotonic()
            # self.flag_lost_control = False
            # self.time_excess_force = time.monotonic()
            # self.flag_excess_force = False
            # self.time_safety_fence = time.monotonic()
            # self.flag_safety_fence = False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/__init__ - {e}')

    def _init_signals(self):
        try:
            self.model.signals.full_cycle_count.connect(self._full_cycle_update)
            self.model.signals.test_launch.connect(self._yellow_btn_push)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_init_signals - {e}')

    def _full_cycle_update(self, command: str):
        try:
            if command == '+1':
                self.count_cycle += 1
            else:
                self.count_cycle = int(command)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_full_cycle_update - {e}')

    def change_flag_repeat(self, flag):
        self.flag_repeat = flag

    def _init_timer_test(self):
        try:
            self.timer_process = QTimer()
            self.timer_process.setInterval(100)
            self.timer_process.timeout.connect(self._update_stage_on_timer)
            self.timer_process.start()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/init_timer - {e}')

    def _update_stage_on_timer(self):
        try:
            stage = self.model.set_regs.get('stage', 'wait')
            test_flag = self.model.set_regs.get('test_flag', False)

            if test_flag is True:
                self._select_alarm_state(self.steps.stage_control_alarm_state())

            if stage == 'wait':
                pass

            # FIXME
            elif stage == 'wait_buffer':
                if self.model.set_regs['buffer_state'][0] == 'OK!':
                    if self.model.set_regs['buffer_state'][1] == 'buffer_on':
                        self.model.set_regs['stage'] = self.model.set_regs.get('next_stage')
                        self.model.reader_start_test()
                        self.model.motor_up(1)

                    elif self.model.set_regs['buffer_state'][1] == 'buffer_off':
                        pass
                        # Ну и в данном случае мы чтото делаем

            elif stage == 'alarm_traverse':
                point = 10
                if self.model.set_regs.get('alarm_tag', '') == 'alarm_traverse_up':
                    point = 10

                elif self.model.set_regs.get('alarm_tag', '') == 'alarm_traverse_down':
                    point = 500

                if self.steps.step_control_traverse_move(point):
                    self.flag_alarm_traverse = True
                    self.model.motor_stop(2)
                    self.model.write_bit_red_light(0)
                    command = {'stage': 'wait',
                               'alarm_flag': False,
                               'alarm_tag': '',
                               }
                    self.model.update_main_dict(command)
                    self.signals.reset_ui.emit()

            elif stage == 'search_hod':
                if self.steps.stage_search_hod(self.count_cycle):
                    self.model.set_regs['stage'] = 'wait'
                    self._stop_gear_min_pos()

            elif stage == 'pos_set_gear':
                if self.steps.stage_pos_set_gear():
                    self.model.set_regs['stage'] = 'wait'
                    self.model.reader_stop_test()
                    self.signals.reset_ui.emit()

            elif stage == 'traverse_referent':
                if self.steps.stage_traverse_referent():
                    self.model.set_regs['stage'] = 'wait'
                    self.traverse_install_point('install')

            elif stage == 'install_amort':
                if self.steps.step_control_traverse_move(self.set_trav_point):
                    self.model.set_regs['stage'] = 'wait'
                    self.signals.wait_yellow_btn.emit()

            elif stage == 'start_point_amort':
                if self.steps.step_control_traverse_move(self.set_trav_point):
                    self.model.set_regs['stage'] = 'wait'
                    self._test_move_cycle()

            elif stage == 'test_move_cycle':
                if self.count_cycle >= 1:
                    self._pumping_before_test()

            elif stage == 'pumping':
                if self.count_cycle >= 3:
                    type_test = self.model.set_regs.get('type_test')
                    if type_test == 'lab_hand':
                        self._test_lab_hand_speed()
                    elif type_test == 'temper':
                        self._test_temper()
                    elif type_test == 'lab_cascade':
                        self._test_lab_cascade()
                    else:
                        self._test_on_two_speed(1)

            elif stage == 'test_speed_one':
                if self.count_cycle >= 5:
                    type_test = self.model.set_regs.get('type_test')
                    if type_test == 'conv':
                        self._result_conveyor_test('one')

                    elif type_test == 'lab':
                        self.signals.lab_save_result.emit('end')

                    self._test_on_two_speed(2)

            elif stage == 'test_speed_two':
                if self.count_cycle >= 5:
                    type_test = self.model.set_regs.get('type_test')
                    if type_test == 'conv':
                        self._result_conveyor_test('two')

                    elif type_test == 'lab':
                        self.signals.lab_save_result.emit('end')

                    command = {'stage': 'wait',
                               'fill_graph': False}
                    self.model.update_main_dict(command)
                    self._stop_gear_end_test()

            elif stage == 'test_lab_hand_speed':
                if self.count_cycle >= 5:
                    command = {'stage': 'wait',
                               'fill_graph': False}
                    self.model.update_main_dict(command)
                    self.signals.lab_save_result.emit('end')
                    self._stop_gear_end_test()

            elif stage == 'test_temper':
                if self.count_cycle >= 1:
                    max_temper = self.model.set_regs.get('temperature', 0)
                    if max_temper < self.model.set_regs.get('finish_temper', 80):
                        max_comp = self.model.set_regs.get('max_comp', 0)
                        max_recoil = self.model.set_regs.get('max_recoil', 0)
                        force = f'{max_recoil}|{max_comp}'
                        self._fill_temper_graph(max_temper, force)
                        self._full_cycle_update('0')

                    else:
                        command = {'stage': 'wait',
                                   'fill_graph': False}
                        self.model.update_main_dict(command)
                        self.signals.lab_save_result.emit('end')
                        self._stop_gear_end_test()

            elif stage == 'test_lab_cascade':
                if self.count_cycle >= 5:
                    self.signals.lab_save_result.emit('cont')
                    if self.cascade < self.max_cascade:
                        speed = self.model.set_regs.get('speed_cascade')[self.cascade]
                        self.model.write_speed_motor(1, speed=speed)
                        command = {'speed': speed,
                                   'force_accum_list': [],
                                   'move_accum_list': [],
                                   'fill_graph': True,
                                   }
                        self.model.update_main_dict(command)

                        self.cascade += 1

                        self._full_cycle_update('0')

                    else:
                        command = {'stage': 'wait',
                                   'fill_graph': False}
                        self.model.update_main_dict(command)
                        self.cascade = 1
                        self.signals.end_test.emit()
                        self._stop_gear_end_test()

            elif stage == 'stop_gear_end_test':
                if self.steps.stage_stop_gear_end_test():
                    self._stop_gear_min_pos()

            elif stage == 'stop_gear_min_pos':
                if self.model.set_regs.get('move') < self.model.main_min_point + 2:
                    self.model.motor_stop(1)

                    command = {'stage': 'wait',
                               'force_accum_list': [],
                               'move_accum_list': [],
                               'start_direction': False,
                               'min_pos': False,
                               'max_pos': False,
                               'test_flag': False,
                               }

                    self.model.update_main_dict(command)

                    if self.model.set_regs.get('search_hod', False):
                        self.model.set_regs['search_hod'] = False
                        self.signals.search_hod_msg.emit()

                    else:
                        if self.model.set_regs.get('type_test') == 'conv':
                            if self.model.set_regs.get('test_launch', False) is True:
                                self.traverse_install_point('install')
                            else:
                                self.traverse_install_point('stop_test')

                        else:
                            self.signals.lab_test_stop.emit()

            elif stage == 'stop_test':
                flag = self.steps.step_control_traverse_move(self.set_trav_point)
                if flag:
                    if not self.model.set_regs.get('alarm_flag', False):
                        self.signals.cancel_test.emit()

                    self.model.set_regs['stage'] = 'wait'

            else:
                pass

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_update_stage_on_timer - {e}')

    def _select_alarm_state(self, tag):
        try:
            if tag == 'lost_control':
                self._lost_control()
            elif tag == 'excess_force':
                self._excess_force()
            elif tag == 'safety_fence':
                self._safety_fence()
            elif tag == 'excess_temperature':
                self._excess_temperature()
            else:
                pass

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_select_alarm_state - {e}')

    def _lost_control(self):
        command = {'stage': 'wait',
                   'alarm_flag': True,
                   'alarm_tag': 'lost_control',
                   'test_launch': False,
                   'test_flag': False}
        self.model.update_main_dict(command)

        self.model.reader_stop_test()

        self.model.write_bit_red_light(1)
        self.model.write_bit_force_cycle(0)

        self.logger.warning(f'lost control')
        self.model.status_bar_msg(f'lost control')
        self.signals.control_msg.emit('lost_control')
        # self.flag_lost_control = False

        # time_signal = time.monotonic()
        # if self.flag_lost_control is False:
        #     self.time_lost_control = time.monotonic()
        #     self.flag_lost_control = True
        #
        # elif 0.3 < abs(self.time_lost_control - time_signal) < 0.5:
        #     self.model.motor_stop(1)
        #     self.model.motor_stop(2)
        #
        #     # self.model.set_regs['stage'] = 'wait'
        #     # self.model.set_regs['alarm_flag'] = True
        #     # self.model.set_regs['test_launch'] = False
        #     # self.model.set_regs['test_flag'] = False
        #
        #     command = {'stage': 'wait',
        #                'alarm_flag': True,
        #                'test_launch': False,
        #                'test_flag': False}
        #     self.model.update_main_dict(command)
        #
        #     self.model.log_error(f'lost control')
        #     self.signals.control_msg.emit('lost_control')
        #     self.flag_lost_control = False
        #
        # elif abs(self.time_lost_control - time_signal) > 0.5:
        #     self.flag_lost_control = False

    def _excess_force(self):
        command = {'stage': 'wait',
                   'alarm_flag': True,
                   'alarm_tag': 'excess_force',
                   'test_launch': False,
                   'test_flag': False}
        self.model.update_main_dict(command)

        self.model.reader_stop_test()

        self.model.write_bit_red_light(1)
        self.model.write_bit_force_cycle(0)

        self.logger.warning(f'excess force')
        self.model.status_bar_msg(f'excess force')
        self.signals.control_msg.emit('excess_force')
        # self.flag_excess_force = False

        # time_signal = time.monotonic()
        # if self.flag_excess_force is False:
        #     self.time_excess_force = time.monotonic()
        #     self.flag_excess_force = True
        #
        # elif 0.3 < abs(self.time_excess_force - time_signal) < 0.5:
        #     self.model.motor_stop(1)
        #     self.model.motor_stop(2)
        #
        #     # self.model.set_regs['stage'] = 'wait'
        #     # self.model.set_regs['alarm_flag'] = True
        #     # self.model.set_regs['test_launch'] = False
        #     # self.model.set_regs['test_flag'] = False
        #
        #     command = {'stage': 'wait',
        #                'alarm_flag': True,
        #                'test_launch': False,
        #                'test_flag': False}
        #     self.model.update_main_dict(command)
        #
        #     self.model.log_error(f'excess force')
        #     self.signals.control_msg.emit('excess_force')
        #     self.flag_excess_force = False
        #
        # elif abs(self.time_excess_force - time_signal) > 0.5:
        #     self.flag_excess_force = False

    def _excess_temperature(self):
        self._stop_gear_end_test()
        self.model.write_bit_red_light(1)

        command = {'alarm_flag': True,
                   'alarm_tag': 'excess_temperature',
                   'test_launch': False,
                   }
        self.model.update_main_dict(command)

        self.logger.warning(f'excess temperature')
        self.model.status_bar_msg(f'excess temperature')
        self.signals.control_msg.emit('excess_temperature')

    def _safety_fence(self):
        command = {'alarm_flag': True,
                   'alarm_tag': 'safety_fence',
                   'test_launch': False,
                   'test_flag': False,
                   }
        self.model.update_main_dict(command)

        self.model.motor_stop(1)
        self.model.motor_stop(2)
        self.model.write_bit_red_light(1)

        self.model.reader_stop_test()

        self.logger.warning(f'safety fence')
        self.model.status_bar_msg(f'safety fence')
        self.signals.control_msg.emit('safety_fence')

        self.model.write_bit_force_cycle(0)

        # if self.flag_safety_fence is False:
        #     self.time_safety_fence = time.monotonic()
        #     self.flag_safety_fence = True
        #
        # # elif 0.1 < abs(self.time_safety_fence - time.monotonic()) < 1:
        # else:
        #
        #     command = {'alarm_flag': True,
        #                'test_launch': False}
        #     self.model.update_main_dict(command)
        #
        #     self._stop_gear_min_pos()
        #
        #     self.model.log_error(f'safety fence')
        #     self.signals.control_msg.emit('safety_fence')
        #     self.flag_safety_fence = False
        #
        # if abs(self.time_excess_force - time.monotonic()) > 2:
        #     self.flag_safety_fence = False

    def _alarm_traverse_position(self, pos):
        self.model.write_bit_red_light(1)

        command = {'stage': 'alarm_traverse',
                   'alarm_flag': True,
                   'alarm_tag': f'alarm_traverse_{pos}',
                   'test_launch': False,
                   'test_flag': False}
        self.model.update_main_dict(command)

        self.model.reader_stop_test()
        self.model.write_bit_force_cycle(0)

        if self.flag_alarm_traverse:
            self.logger.warning(f'alarm traverse {pos}')
            self.model.status_bar_msg(f'alarm traverse {pos}')
            self.signals.control_msg.emit(f'alarm_traverse_{pos}')
            self.flag_alarm_traverse = False

    def _position_traverse(self):
        self.signals.control_msg.emit(f'pos_traverse')

    def _move_detection(self):
        self.signals.control_msg.emit(f'move_detection')

    def _gear_set_pos(self):
        self.signals.control_msg.emit('gear_set_pos')

    def _pumping_msg(self):
        self.signals.control_msg.emit(f'pumping')

    def work_interrupted_operator(self):
        command = {'stage': 'wait',
                   'test_launch': False,
                   'test_flag': False}
        self.model.update_main_dict(command)

        self.model.lamp_all_switch_off()

        if self.model.client.set_dict['connect']:
            self.model.motor_stop(1)
            self.model.motor_stop(2)
            self.model.reader_stop_test()
            self.model.write_bit_force_cycle(0)

    def _yellow_btn_push(self, state: bool):
        """Обработка нажатия жёлтой кнопки, запускает она испытание или останавливает"""
        try:
            if state:
                if self.model.set_regs.get('test_flag', False) is False:
                    if self.model.set_regs.get('green_light') or self.model.set_regs.get('red_light'):
                        self.model.lamp_all_switch_off()

                    command = {'alarm_flag': False,
                               'alarm_tag': '',
                               'test_flag': True,
                               'fill_graph': False,
                               'force_accum_list': [],
                               'move_accum_list': [],
                               'force_graph': [],
                               'move_real_list': [],
                               'min_pos': False,
                               'max_pos': False,
                               'start_direction': False}
                    self.model.update_main_dict(command)
                    self.model.reset_min_point()

                    if self.model.set_regs.get('lost_control'):
                        self.model.write_bit_unblock_control()

                    if self.model.set_regs.get('excess_force'):
                        self.model.write_bit_emergency_force()

                    self.traverse_install_point('start_test')

                else:
                    self.model.set_regs['test_flag'] = False
                    self.stop_test_clicked()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_yellow_btn_push - {e}')

    def start_test_clicked(self):
        """
        Точка входа в испытание, определение референтной точки траверсы, если известна,
        то сразу запуск позиционирования для установки амортизатора
        """
        try:
            if self.model.set_regs.get('excess_force', False) is True:
                self.model.write_bit_emergency_force()

            if self.model.set_regs.get('lost_control', False) is True:
                self.model.write_bit_unblock_control()

            self.model.lamp_all_switch_off()

            command = {'test_launch': True,
                       'test_flag': False,
                       'fill_graph': False,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'force_graph': [],
                       'move_real_list': [],
                       'max_temperature': 0,
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       }

            self.model.update_main_dict(command)
            self.model.reset_min_point()

            amort = self.model.set_regs.get('amort')
            self.model.write_emergency_force(self.calc_data.excess_force(amort))

            if self.flag_repeat:
                # FIXME
                self.flag_repeat = False
                type_test = self.model.set_regs.get('type_test')
                self.model.reader_start_test()
                if type_test == 'lab_hand':
                    self._test_lab_hand_speed()

                elif type_test == 'temper':
                    self._test_temper()

                elif type_test == 'lab_cascade':
                    self._test_lab_cascade()

                else:
                    self._test_on_two_speed(1)

            else:
                if self.model.set_regs.get('traverse_move', 0) < 10:
                    self._traverse_referent_point()

                else:
                    self.traverse_install_point('install')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/start_test_clicked - {e}')

    def stop_test_clicked(self):
        """
        Завершение теста, если определена референтная точка коленвала, то остановка в нижней точке,
        иначе моментальная остановка
        """
        try:
            command = {'stage': 'wait',
                       'test_launch': False,
                       'fill_graph': False,
                       'test_flag': False,
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       }

            self.model.update_main_dict(command)

            if self.model.set_regs.get('gear_referent', False):
                self._stop_gear_end_test()
            else:
                self.model.motor_stop(1)
                self.model.motor_stop(2)

                self.signals.cancel_test.emit()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/stop_test_clicked - {e}')

    def search_hod_gear(self):
        try:
            hod = self.model.set_regs.get('hod', 120)
            if hod > 100:
                speed = 0.03
            elif 50 < hod <= 100:
                speed = 0.02
            else:
                speed = 0.01

            command = {'stage': 'wait',
                       'search_hod': True,
                       'test_launch': False,
                       'test_flag': False,
                       'fill_graph': False,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       'next_stage': 'search_hod',
                       }
            self.model.update_main_dict(command)

            self._move_detection()
            self.model.write_speed_motor(1, speed=speed)
            self._full_cycle_update('0')
            self.model.set_regs['stage'] = 'wait_buffer'
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/search_hod_gear - {e}')

    def move_gear_set_pos(self):
        try:
            hod = self.model.set_regs.get('hod', 120)
            if hod > 100:
                speed = 0.03
            elif 50 < hod <= 100:
                speed = 0.02
            else:
                speed = 0.01

            command = {'stage': 'wait',
                       'test_launch': False,
                       'test_flag': False,
                       'fill_graph': False,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       'next_stage': 'pos_set_gear',
                       }
            self.model.update_main_dict(command)
            self._gear_set_pos()
            self.model.write_speed_motor(1, speed=speed)
            self._full_cycle_update('0')
            self.model.set_regs['stage'] = 'wait_buffer'
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/move_gear_set_pos - {e}')

    def _traverse_referent_point(self):
        """Подъём траверсы до концевика для определения референтной точки"""
        try:
            self.signals.traverse_referent_msg.emit()
            self.model.write_speed_motor(2, freq=20)
            self.model.set_regs['stage'] = 'traverse_referent'

            self.model.motor_up(2)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_traverse_referent_point - {e}')

    def traverse_install_point(self, tag):
        """Позционирование траверсы"""
        try:
            amort = self.model.set_regs.get('amort')
            stock_point = self.model.set_regs.get('traverse_stock', 756)
            hod = amort.hod
            len_min = amort.min_length
            len_max = amort.max_length
            mid_point = (len_max - len_min) / 2
            adapter = amort.adapter_len

            if tag == 'install':
                install_point = int((stock_point + hod / 2) - len_max - adapter)
                self._position_traverse()
                pos_trav = float(self.model.set_regs.get('traverse_move'))
                if abs(pos_trav - install_point) < 2:
                    self.signals.wait_yellow_btn.emit()

                else:
                    self.model.set_regs['stage'] = 'install_amort'
                    self.set_trav_point = install_point
                    self.steps.step_traverse_move_position(install_point)

            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self._position_traverse()
                self.model.set_regs['stage'] = 'start_point_amort'
                self.set_trav_point = start_point
                self.steps.step_traverse_move_position(start_point)

            elif tag == 'stop_test':
                if not self.model.set_regs.get('alarm_flag', False):
                    self._position_traverse()

                end_point = int((stock_point + hod / 2) - len_max - adapter)

                self.model.set_regs['stage'] = 'stop_test'
                self.set_trav_point = end_point
                self.steps.step_traverse_move_position(end_point)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/traverse_install_point - {e}')

    def _test_move_cycle(self):
        """Проверочный ход"""
        try:
            self._move_detection()
            hod = self.model.set_regs.get('hod', 120)
            if hod > 100:
                speed = 0.07
            elif 50 < hod <= 100:
                speed = 0.05
            else:
                speed = 0.03

            self.model.write_speed_motor(1, speed=speed)
            self.model.set_regs['next_stage'] = 'test_move_cycle'
            self.model.set_regs['stage'] = 'wait_buffer'
            self._full_cycle_update('0')
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_move_cycle - {e}')

    def _pumping_before_test(self):
        """Прокачка на скорости 0.2 3 оборота перед запуском теста"""
        try:
            self._pumping_msg()
            hod = self.model.set_regs.get('hod', 120)
            if hod >= 100:
                speed = 0.2
            elif 50 < hod <= 100:
                speed = 0.1
            else:
                speed = 0.03
            
            self.model.write_speed_motor(1, speed=speed)

            self.model.set_regs['stage'] = 'pumping'

            self._full_cycle_update('0')
            self.model.motor_up(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_pumping_before_test - {e}')

    def _test_on_two_speed(self, ind):
        try:
            type_test = self.model.set_regs.get('type_test')
            if type_test == 'conv':
                self.signals.conv_win_test.emit()
            elif type_test == 'lab':
                self.signals.lab_win_test.emit()

            speed_one = self.model.set_regs.get('amort').speed_one
            speed_two = self.model.set_regs.get('amort').speed_two

            if ind == 1:
                self.model.write_speed_motor(1, speed=speed_one)
                command = {'speed': speed_one,
                           'stage': 'test_speed_one',
                           'force_accum_list': [],
                           'move_accum_list': [],
                           'fill_graph': True,
                           }
                self.model.update_main_dict(command)

                self.model.motor_up(1)

            elif ind == 2:
                command = {'speed': speed_two,
                           'stage': 'test_speed_two',
                           }
                self.model.update_main_dict(command)

                self.model.write_speed_motor(1, speed=speed_two)

            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_on_two_speed - {e}')

    def _test_lab_hand_speed(self):
        try:
            self.signals.lab_win_test.emit()
            speed = self.model.set_regs.get('speed')
            self.model.write_speed_motor(1, speed=speed)
            command = {'stage': 'test_lab_hand_speed',
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            self.model.motor_up(1)

            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_lab_hand_speed - {e}')

    def _test_temper(self):
        try:
            self.signals.lab_win_test.emit()
            speed = self.model.set_regs.get('speed')
            self.model.write_speed_motor(1, speed=speed)
            command = {'stage': 'test_temper',
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'temper_graph': [],
                       'temper_force_graph': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            self.model.motor_up(1)

            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_temper - {e}')

    def _fill_temper_graph(self, temper, force):
        try:
            temper_graph = self.model.set_regs.get('temper_graph', [])
            temper_graph.append(temper)

            force_graph = self.model.set_regs.get('temper_force_graph', [])
            force_graph.append(force)

            self.model.set_regs['temper_graph'] = temper_graph[:]
            self.model.set_regs['temper_force_graph'] = force_graph[:]

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_fill_temper_graph - {e}')

    def _result_conveyor_test(self, speed):
        """Включение индикаторов, зелёный - в допусках, красный - нет"""
        try:
            comp = self.model.set_regs.get('max_comp', 0)
            recoil = self.model.set_regs.get('max_recoil', 0)
            amort = self.model.set_regs.get('amort')
            min_comp, max_comp = 0, 2000
            min_recoil, max_recoil = 0, 2000

            if speed == 'one':
                min_comp, max_comp = amort.min_comp, amort.max_comp
                min_recoil, max_recoil = amort.min_recoil, amort.max_recoil

            elif speed == 'two':
                min_comp, max_comp = amort.min_comp_2, amort.max_comp_2
                min_recoil, max_recoil = amort.min_recoil_2, amort.max_recoil_2

            if min_comp < comp < max_comp and min_recoil < recoil < max_recoil:
                self.model.lamp_green_switch_on()

            else:
                self.model.lamp_red_switch_on()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_result_conveyor_test - {e}')

    def _test_lab_cascade(self):
        try:
            self.signals.lab_win_test.emit()
            speed_list = self.model.set_regs.get('speed_cascade')
            self.cascade = 1
            self.max_cascade = len(speed_list)
            self.model.write_speed_motor(1, speed=speed_list[0])
            command = {'speed': speed_list[0],
                       'stage': 'test_lab_cascade',
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            self._full_cycle_update('0')

            self.model.motor_up(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_lab_cascade - {e}')

    def _stop_gear_end_test(self):
        """Остановка двигателя после испытания и перед исходным положением"""
        try:
            self.model.motor_stop(1)

            self.model.set_regs['stage'] = 'stop_gear_end_test'

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_stop_gear_end_test - {e}')

    def _stop_gear_min_pos(self):
        """Снижение скорости и остановка привода в нижней точке"""
        try:
            self.model.reader_stop_test()
            self.model.write_bit_force_cycle(0)

            hod = self.model.set_regs.get('hod', 120)
            if hod > 100:
                speed = 0.03
            elif 50 < hod <= 100:
                speed = 0.02
            else:
                speed = 0.01

            self.model.write_speed_motor(1, speed=speed)

            self.model.motor_up(1)

            self.model.set_regs['stage'] = 'stop_gear_min_pos'

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_stop_gear_min_pos - {e}')
