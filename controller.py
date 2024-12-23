# -*- coding: utf-8 -*-
import time
from functools import reduce
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class ControlSignals(QObject):
    control_msg = pyqtSignal(str)
    traverse_referent = pyqtSignal()
    wait_yellow_btn = pyqtSignal()
    test_move_cycle = pyqtSignal()
    conv_win_test = pyqtSignal()
    conv_lamp = pyqtSignal(str)
    lab_win_test = pyqtSignal()
    lab_test_stop = pyqtSignal()
    lab_save_result = pyqtSignal(str)
    cancel_test = pyqtSignal()
    end_test = pyqtSignal()
    search_hod = pyqtSignal()
    reset_ui = pyqtSignal()


class Controller:
    def __init__(self, model):
        try:
            self.signals = ControlSignals()
            self.model = model

            self.response = {}
            self.timer_process = None
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self.count_wait_point = 0
            self.flag_alarm_traverse = True
            self.stop_point = 0
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
            self.model.log_error(f'ERROR in controller/__init__ - {e}')

    def _init_signals(self):
        try:
            self.model.signals.full_cycle_count.connect(self._update_full_cycle)
            self.model.signals.test_launch.connect(self._yellow_btn_push)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_init_signals - {e}')

    def update_data_ctrl(self, response):
        try:
            self.response = {**self.response, **response}

        except Exception as e:
            self.model.log_error(f'ERROR in controller/update_data - {e}')

    def _update_full_cycle(self):
        try:
            self.count_cycle += 1

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_update_full_cycle - {e}')

    def change_flag_repeat(self, flag):
        self.flag_repeat = flag

    def _init_timer_test(self):
        try:
            self.timer_process = QTimer()
            self.timer_process.setInterval(100)
            self.timer_process.timeout.connect(self._update_stage_on_timer)
            self.timer_process.start()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/init_timer - {e}')

    def _update_stage_on_timer(self):
        try:
            stage = self.response.get('stage')
            test_flag = self.response.get('test_flag')

            # self._control_alarm_traverse_position()

            if test_flag is True:
                self._control_alarm_state()

            if stage == 'wait':
                pass

            elif stage == 'alarm_traverse':
                if self.response.get('alarm_tag', '') == 'alarm_traverse_up':
                    self.set_trav_point = 10

                elif self.response.get('alarm_tag', '') == 'alarm_traverse_down':
                    self.set_trav_point = 500

                flag = self._control_traverse_move()

                if flag:
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
                if self.count_cycle >= 1:
                    self.model.motor_stop(1)
                    hod = round(abs(self.response.get('min_point')) + abs(self.response.get('max_point')), 1)

                    command = {'stage': 'wait',
                               'hod_measure': hod,
                               }
                    self.model.update_main_dict(command)

                    self._stop_gear_min_pos()

            elif stage == 'pos_set_gear':
                if self.response.get('gear_referent', False):
                    if self.response.get('max_pos', False):
                        if abs(14 - self.response.get('move', 200)) < 5:
                            self.model.motor_stop(1)
                            command = {'stage': 'wait',
                                       'max_pos': False,
                                       }
                            self.model.update_main_dict(command)

                            self.model.reader_stop_test()
                            # time.sleep(0.2)
                            # self.model.write_bit_force_cycle(0)

                            self.signals.reset_ui.emit()

            elif stage == 'traverse_referent':
                if self.response.get('highest_position', False) is True:
                    self.model.motor_stop(2)

                    command = {'traverse_referent': True,
                               'stage': 'wait'}
                    self.model.update_main_dict(command)
                    self.traverse_install_point('install')

            elif stage == 'install_amort':
                flag = self._control_traverse_move()
                if flag:

                    command = {'traverse_freq': 10,
                               'stage': 'wait'}
                    self.model.update_main_dict(command)

                    self.signals.wait_yellow_btn.emit()

            elif stage == 'start_point_amort':
                flag = self._control_traverse_move()
                if flag:

                    command = {'traverse_freq': 10,
                               'stage': 'wait'}
                    self.model.update_main_dict(command)

                    self._test_move_cycle()

            elif stage == 'test_move_cycle':
                if self.count_cycle >= 1:
                    # self.model.motor_stop(1)
                    self._pumping_before_test()

            elif stage == 'pumping':
                if self.count_cycle >= 3:
                    type_test = self.response.get('type_test')
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
                    type_test = self.response.get('type_test')
                    if type_test == 'conv':
                        max_comp = self.response.get('max_comp')
                        max_recoil = self.response.get('max_recoil')
                        self._result_conveyor_test('one', max_comp, max_recoil)

                    elif type_test == 'lab':
                        self.signals.lab_save_result.emit('end')

                    self._test_on_two_speed(2)

            elif stage == 'test_speed_two':
                if self.count_cycle >= 5:
                    type_test = self.response.get('type_test')
                    if type_test == 'conv':
                        max_comp = self.response.get('max_comp')
                        max_recoil = self.response.get('max_recoil')
                        self._result_conveyor_test('two', max_comp, max_recoil)

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
                    max_temper = self.response.get('temperature')
                    if max_temper < self.response.get('finish_temper', 80):
                        max_comp = self.response.get('max_comp')
                        max_recoil = self.response.get('max_recoil')
                        force = f'{max_recoil}|{max_comp}'
                        self._fill_temper_graph(max_temper, force)
                        self.count_cycle = 0

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
                        speed = self.response.get('speed_cascade')[self.cascade]
                        self._write_speed_motor(1, speed=speed)
                        command = {'speed': speed,
                                   'force_accum_list': [],
                                   'move_accum_list': [],
                                   'fill_graph': True,
                                   }
                        self.model.update_main_dict(command)

                        self.cascade += 1

                        self.count_cycle = 0

                    else:
                        command = {'stage': 'wait',
                                   'fill_graph': False}
                        self.model.update_main_dict(command)
                        self.cascade = 1
                        self.signals.end_test.emit()
                        self._stop_gear_end_test()

            elif stage == 'stop_gear_end_test':
                move_list = self.response.get('move_list')
                stop_point = reduce(lambda x, y: round(abs(abs(x) - abs(y)), 3), move_list)

                if stop_point < 0.2 or stop_point == move_list[0]:  # Перемещение перестало изменяться
                    self.count_wait_point += 1

                else:
                    self.count_wait_point = 0

                if self.count_wait_point > 3:
                    self.count_wait_point = 0
                    self.model.update_main_dict({'stage': 'wait'})
                    self._stop_gear_min_pos()

            elif stage == 'stop_gear_min_pos':
                if self.response.get('move') < self.model.main_min_point + 2:
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

                    if self.response.get('search_hod', False):
                        self.model.update_main_dict({'search_hod': False})
                        self.signals.search_hod.emit()

                    if self.response.get('type_test') == 'conv':
                        if self.response.get('test_launch', False) is True:
                            self.traverse_install_point('install')
                        else:
                            self.traverse_install_point('stop_test')

                    else:
                        self.signals.lab_test_stop.emit()

            elif stage == 'stop_test':
                flag = self._control_traverse_move()
                if flag:
                    if not self.response.get('alarm_flag', False):
                        self.signals.cancel_test.emit()

                    command = {'stage': 'wait',
                               'traverse_freq': 8}

                    self.model.update_main_dict(command)

            else:
                pass

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_update_stage_on_timer - {e}')

    def _control_traverse_move(self) -> bool:  # Функция отслеживания траверсы, при достижении точки останов
        try:
            if 5 < abs(self.set_trav_point - self.response.get('traverse_move')) <= 10:
                if not self.flag_freq_1_step:
                    self._write_speed_motor(2, freq=15)
                    self.flag_freq_1_step = True

            if 1 < abs(self.set_trav_point - float(self.response.get('traverse_move'))) <= 5:
                if not self.flag_freq_2_step:
                    self._write_speed_motor(2, freq=10)
                    self.flag_freq_2_step = True

            if abs(self.set_trav_point - self.response.get('traverse_move')) <= 1:
                self.model.motor_stop(2)
                return True

            return False

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_control_traverse_move - {e}')

    def _control_switch_traverse_position(self):
        try:
            if self.response.get('type_test') == 'hand':
                self.model.motor_stop(2)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_control_switch_traverse_position - {e}')

    def _control_alarm_traverse_position(self):
        try:
            if self.response.get('alarm_highest_position', True) is False:
                self._alarm_traverse_position('up')
            if self.response.get('alarm_lowest_position', True) is False:
                self._alarm_traverse_position('down')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_control_alarm_traverse_position - {e}')

    def move_traverse_out_alarm(self, pos):
        try:
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self._write_speed_motor(2, freq=10)
            if pos == 'up':
                self.model.motor_down(2)

            elif pos == 'down':
                self.model.motor_up(2)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/move_traverse_out_alarm - {e}')

    def _control_alarm_state(self):
        try:
            if not self.response.get('type_test') == 'temper':
                if self.response.get('max_temperature', 0) >= self.response.get('amort').max_temper:
                    self._excess_temperature()

            if self.response.get('lost_control', False) is True:
                self._lost_control()
            if self.response.get('excess_force', False) is True:
                self._excess_force()
            if self.response.get('safety_fence', False) is True:
                self._safety_fence()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_control_alarm_state - {e}')

    def _lost_control(self):
        command = {'stage': 'wait',
                   'alarm_flag': True,
                   'alarm_tag': 'lost_control',
                   'test_launch': False,
                   'test_flag': False}
        self.model.update_main_dict(command)

        self.model.reader_stop_test()

        self.model.write_bit_red_light(1)
        # self.model.write_bit_force_cycle(0)

        self.model.log_error(f'lost control')
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
        # self.model.write_bit_force_cycle(0)

        self.model.log_error(f'excess force')
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

        self.model.log_error(f'excess temperature')
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

        self.model.log_error(f'safety fence')
        self.signals.control_msg.emit('safety_fence')

        # self.model.write_bit_force_cycle(0)

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
        # time.sleep(0.2)
        # self.model.write_bit_force_cycle(0)

        if self.flag_alarm_traverse:
            self.model.log_error(f'alarm traverse {pos}')
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

        self.lamp_all_switch_off()

        if self.model.client:
            self.model.motor_stop(1)
            self.model.motor_stop(2)
            self.model.reader_stop_test()
            # time.sleep(0.2)
            # self.model.write_bit_force_cycle(0)

    def _yellow_btn_push(self, state: bool):
        """Обработка нажатия жёлтой кнопки, запускает она испытание или останавливает"""
        try:
            if state:
                if self.response.get('test_flag', False) is False:
                    if self.response.get('green_light') or self.response.get('red_light'):
                        self.lamp_all_switch_off()
                        time.sleep(0.2)

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

                    if self.response.get('lost_control'):
                        self.model.write_bit_unblock_control()

                    if self.response.get('excess_force'):
                        self.model.write_bit_emergency_force()

                    self.traverse_install_point('start_test')

                else:
                    self.model.update_main_dict({'test_flag': False})
                    self.stop_test_clicked()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_yellow_btn_push - {e}')

    def _write_speed_motor(self, adr: int, speed: float = None, freq: int = None):
        """
        Запись скорости вращения двигателя, если задана скорость, то она пересчитывается в частоту,
        частота записывается напрямую
        """
        try:
            value = 0
            if not freq:
                value = self.model.calculate_freq(speed)
            elif not speed:
                value = 100 * freq

            self.model.write_frequency(adr, value)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_write_speed_motor - {e}')

    def start_test_clicked(self):
        """
        Точка входа в испытание, определение референтной точки траверсы, если известна,
        то сразу запуск позиционирования для установки амортизатора
        """
        try:
            if self.response.get('excess_force', False) is True:
                self.model.write_bit_emergency_force()

            if self.response.get('lost_control', False) is True:
                self.model.write_bit_unblock_control()

            self.lamp_all_switch_off()
            # self.model.write_bit_force_cycle(1)

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

            force = self._calc_excess_force()
            self.model.write_emergency_force(force)

            if self.flag_repeat:
                self.flag_repeat = False
                type_test = self.response.get('type_test')
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
                if self.response.get('traverse_move', 0) < 10:
                    self._traverse_referent_point()

                else:
                    self.traverse_install_point('install')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/start_test_clicked - {e}')

    def stop_test_clicked(self):
        """
        Завершение теста, если определена референтная коленвала, то остановка в нижней точке,
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

            if self.response.get('gear_referent'):
                self._stop_gear_end_test()
            else:
                self.model.motor_stop(1)
                self.model.motor_stop(2)

                self.signals.cancel_test.emit()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/stop_test_clicked - {e}')

    def search_hod_gear(self):
        try:
            # self.model.write_bit_force_cycle(1)
            hod = self.response.get('hod', 120)
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
                       }

            self.model.update_main_dict(command)

            self._move_detection()

            self._write_speed_motor(1, speed=speed)

            self.count_cycle = 0

            self.model.reader_start_test()

            self.model.update_main_dict({'stage': 'search_hod'})

            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/search_hod_gear - {e}')

    def move_gear_set_pos(self):
        try:
            # self.model.write_bit_force_cycle(1)
            hod = self.response.get('hod', 120)
            if hod > 100:
                speed = 0.03
            elif 50 < hod <= 100:
                speed = 0.02
            else:
                speed = 0.01

            command = {'stage': 'wait',
                       'search_hod': False,
                       'test_launch': False,
                       'test_flag': False,
                       'fill_graph': False,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       }
            self.model.update_main_dict(command)

            self._gear_set_pos()

            self._write_speed_motor(1, speed=speed)

            self.count_cycle = 0

            self.model.reader_start_test()

            self.model.update_main_dict({'stage': 'pos_set_gear'})

            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/move_gear_set_pos - {e}')

    def _traverse_move_position(self, set_point):
        """Непосредственно включение и перемещение траверсы"""
        try:
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self._write_speed_motor(2, freq=20)
            self.model.update_main_dict({'traverse_freq': 20})
            self.set_trav_point = float(set_point)
            pos_trav = self.response.get('traverse_move')

            if pos_trav > self.set_trav_point:
                self.model.motor_up(2)
            else:
                self.model.motor_down(2)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_traverse_move_position - {e}')

    def _traverse_referent_point(self):
        """Подъём траверсы до концевика для определения референтной точки"""
        try:
            self.signals.traverse_referent.emit()
            self._write_speed_motor(2, freq=20)
            command = {'traverse_freq': 20,
                       'stage': 'traverse_referent'}
            self.model.update_main_dict(command)
            self.model.motor_up(2)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_traverse_referent_point - {e}')

    def traverse_install_point(self, tag):
        """Позционирование траверсы"""
        try:
            amort = self.response.get('amort')
            stock_point = self.response.get('traverse_stock')
            hod = amort.hod
            len_min = amort.min_length
            len_max = amort.max_length
            mid_point = (len_max - len_min) / 2
            adapter = amort.adapter_len

            if tag == 'install':
                install_point = int((stock_point + hod / 2) - len_max - adapter)
                self._position_traverse()
                pos_trav = float(self.response.get('traverse_move'))
                if abs(pos_trav - install_point) < 2:
                    self.signals.wait_yellow_btn.emit()

                else:
                    self.model.update_main_dict({'stage': 'install_amort'})
                    self._traverse_move_position(install_point)

            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self._position_traverse()
                self.model.update_main_dict({'stage': 'start_point_amort'})
                self._traverse_move_position(start_point)

            elif tag == 'stop_test':
                if not self.response.get('alarm_flag', False):
                    self._position_traverse()

                end_point = int((stock_point + hod / 2) - len_max - adapter)

                self.model.update_main_dict({'stage': 'stop_test'})
                self._traverse_move_position(end_point)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/traverse_install_point - {e}')

    def _test_move_cycle(self):
        """Проверочный ход"""
        try:
            # self.model.write_bit_force_cycle(1)
            self._move_detection()
            hod = self.response.get('hod', 120)
            if hod > 100:
                speed = 0.07
            elif 50 < hod <= 100:
                speed = 0.05
            else:
                speed = 0.03

            self._write_speed_motor(1, speed=speed)

            self.model.update_main_dict({'stage': 'test_move_cycle'})

            self.count_cycle = 0

            self.model.reader_start_test()

            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_test_move_cycle - {e}')

    def _calc_excess_force(self):
        try:
            amort = self.response.get('amort')
            force = int(max(amort.max_comp, amort.max_recoil) * 4)
            if force >= 2000:
                return 2000
            if force // 100 == 0:
                return 100
            else:
                return (force // 100) * 100 + 100

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_calc_excess_force - {e}')

    def _pumping_before_test(self):
        """Прокачка на скорости 0.2 3 оборота перед запуском теста"""
        try:
            self._pumping_msg()
            hod = self.response.get('hod', 120)
            if hod >= 100:
                speed = 0.2
            elif 50 < hod <= 100:
                speed = 0.1
            else:
                speed = 0.03
            
            self._write_speed_motor(1, speed=speed)

            self.model.update_main_dict({'stage': 'pumping'})

            self.count_cycle = 0
            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_pumping_before_test - {e}')

    def _test_on_two_speed(self, ind):
        try:
            type_test = self.response.get('type_test')
            if type_test == 'conv':
                self.signals.conv_win_test.emit()
            elif type_test == 'lab':
                self.signals.lab_win_test.emit()

            speed_one = self.response.get('amort').speed_one
            speed_two = self.response.get('amort').speed_two

            if ind == 1:
                self._write_speed_motor(1, speed=speed_one)
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

                self._write_speed_motor(1, speed=speed_two)

            self.count_cycle = 0

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_test_on_two_speed - {e}')

    def _test_lab_hand_speed(self):
        try:
            self.signals.lab_win_test.emit()
            speed = self.response.get('speed')
            self._write_speed_motor(1, speed=speed)
            command = {'stage': 'test_lab_hand_speed',
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            self.model.motor_up(1)

            self.count_cycle = 0

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_test_lab_hand_speed - {e}')

    def _test_temper(self):
        try:
            self.signals.lab_win_test.emit()
            speed = self.response.get('speed')
            self._write_speed_motor(1, speed=speed)
            command = {'stage': 'test_temper',
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'temper_graph': [],
                       'temper_force_graph': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            self.model.motor_up(1)

            self.count_cycle = 0

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_test_temper - {e}')

    def _fill_temper_graph(self, temper, force):
        try:
            temper_graph = self.response.get('temper_graph', [])
            temper_graph.append(temper)

            force_graph = self.response.get('temper_force_graph', [])
            force_graph.append(force)

            self.model.update_main_dict({'temper_graph': temper_graph})
            self.model.update_main_dict({'temper_force_graph': force_graph})

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_fill_temper_graph - {e}')

    def _result_conveyor_test(self, speed, comp, recoil):
        """Включение индикаторов, зелёный - в допусках, красный - нет"""
        try:
            amort = self.response.get('amort')
            min_comp, max_comp = 0, 2000
            min_recoil, max_recoil = 0, 2000

            if speed == 'one':
                min_comp, max_comp = amort.min_comp, amort.max_comp
                min_recoil, max_recoil = amort.min_recoil, amort.max_recoil

            elif speed == 'two':
                min_comp, max_comp = amort.min_comp_2, amort.max_comp_2
                min_recoil, max_recoil = amort.min_recoil_2, amort.max_recoil_2

            if min_comp < comp < max_comp and min_recoil < recoil < max_recoil:
                self.lamp_green_switch_on()

            else:
                self.lamp_red_switch_on()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_result_conveyor_test - {e}')

    def _test_lab_cascade(self):
        try:
            self.signals.lab_win_test.emit()
            speed_list = self.response.get('speed_cascade')
            self.cascade = 1
            self.max_cascade = len(speed_list)
            self._write_speed_motor(1, speed=speed_list[0])
            command = {'speed': speed_list[0],
                       'stage': 'test_lab_cascade',
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            self.count_cycle = 0

            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_test_lab_cascade - {e}')

    def _stop_gear_end_test(self):
        """Остановка двигателя после испытания и перед исходным положением"""
        try:
            self.model.motor_stop(1)

            self.model.update_main_dict({'stage': 'stop_gear_end_test'})

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_stop_gear_end_test - {e}')

    def _stop_gear_min_pos(self):
        """Снижение скорости и остановка привода в нижней точке"""
        try:
            self.model.reader_stop_test()
            # time.sleep(0.2)
            # self.model.write_bit_force_cycle(0)

            hod = self.response.get('hod', 120)
            if hod > 100:
                speed = 0.03
            elif 50 < hod <= 100:
                speed = 0.02
            else:
                speed = 0.01

            self._write_speed_motor(1, speed=speed)

            self.model.motor_up(1)

            self.model.update_main_dict({'stage': 'stop_gear_min_pos'})

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_stop_gear_min_pos - {e}')

    def lamp_all_switch_on(self):
        """Включение всех индикаторов"""
        try:
            if not self.response.get('green_light'):
                self.model.write_bit_green_light(1)
            if not self.response.get('red_light'):
                self.model.write_bit_red_light(1)
            self.signals.conv_lamp.emit('all_on')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/lamp_all_switch_on - {e}')

    def lamp_all_switch_off(self):
        """Выключение всех индикаторов"""
        try:
            if self.response.get('green_light'):
                self.model.write_bit_green_light(0)
            if self.response.get('red_light'):
                self.model.write_bit_red_light(0)
            self.signals.conv_lamp.emit('all_off')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/lamp_all_switch_off - {e}')

    def lamp_green_switch_on(self):
        """Выключение зелёного индикатора"""
        try:
            if not self.response.get('green_light'):
                self.model.write_bit_green_light(1)
            if self.response.get('red_light'):
                self.model.write_bit_red_light(0)
            self.signals.conv_lamp.emit('green_on')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/lamp_green_switch_on - {e}')

    def lamp_red_switch_on(self):
        """Выключение красного индикатора"""
        try:
            if self.response.get('green_light'):
                self.model.write_bit_green_light(0)
            if not self.response.get('red_light'):
                self.model.write_bit_red_light(1)
            self.signals.conv_lamp.emit('red_on')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/lamp_red_switch_on - {e}')
