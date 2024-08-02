# -*- coding: utf-8 -*-
import os
import time
from functools import reduce
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class ControlSignals(QObject):
    control_msg = pyqtSignal(str)
    traverse_referent = pyqtSignal()
    traverse_position = pyqtSignal()
    wait_yellow_btn = pyqtSignal()
    test_move_cycle = pyqtSignal()
    conv_win_test = pyqtSignal()
    conv_test_cancel = pyqtSignal()
    conv_lamp = pyqtSignal(str)
    lab_win_test = pyqtSignal()
    lab_test_cancel = pyqtSignal()
    cancel_test = pyqtSignal()
    search_hod = pyqtSignal()
    reset_ui = pyqtSignal()


class Controller:
    def __init__(self, model):
        try:
            self.signals = ControlSignals()
            self.response = {}
            self.timer_process = None
            self.timer_unblock = None
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self.count_wait_point = 0
            self.flag_alarm_traverse = True
            self.stop_point = 0
            self.count_cycle = 0
            self.set_trav_point = 0
            # self.time_start_wait = None
            # self.time_all_wait = None
            # self.time_tag_wait = None
            # self.time_lost_control = time.monotonic()
            # self.flag_lost_control = False
            # self.time_excess_force = time.monotonic()
            # self.flag_excess_force = False
            # self.time_safety_fence = time.monotonic()
            # self.flag_safety_fence = False

            self.model = model

            self._start_param_ctrl()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/__init__ - {e}')

    def _start_param_ctrl(self):
        try:
            self._init_signals()
            self._init_timer_test()
            self.timer_process.start()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_start_param_ctrl - {e}')

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

    def _init_timer_test(self):
        try:
            self.timer_process = QTimer()
            self.timer_process.setInterval(100)
            self.timer_process.timeout.connect(self._update_stage_on_timer)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/init_timer - {e}')

    def _update_stage_on_timer(self):
        try:
            stage = self.response.get('stage')
            test_flag = self.response.get('test_flag')

            # if self.flag_alarm_traverse:
            #     self.flag_alarm_traverse = False
            #     self._control_alarm_traverse_position()

            # self._control_switch_traverse_position()

            if test_flag is True:
                self._control_alarm_state()

            if stage == 'wait':
                pass

            elif stage == 'alarm_traverse':
                if self.response.get('alarm_tag', '') == 'alarm_traverse_up':
                    if not self.response.get('highest_position', True) or self.response.get('traverse_move', -10) > 0:
                        self.flag_alarm_traverse = True
                        self.model.motor_stop(2)
                        self.model.write_bit_red_light(0)
                        command = {'stage': 'wait',
                                   'alarm_flag': False,
                                   'alarm_tag': '',
                                   }
                        self.model.update_main_dict(command)
                        self.signals.reset_ui.emit()

                elif self.response.get('alarm_tag', '') == 'alarm_traverse_down':
                    if not self.response.get('lowest_position', True) or self.response.get('traverse_move', 600) < 550:
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
                if self.count_cycle >= 2:
                    self.model.motor_stop(1)
                    self.model.set_regs['stage'] = 'wait'
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

                            self.signals.reset_ui.emit()

            elif stage == 'traverse_referent':
                if self.response.get('highest_position', False) is True:
                    self.model.motor_stop(2)
                    # time.sleep(0.2)
                    command = {'traverse_referent': True,
                               'stage': 'wait'}
                    self.model.update_main_dict(command)
                    self._traverse_install_point('install')

            elif stage == 'install_amort':
                if 5 < abs(self.set_trav_point - float(self.response.get('traverse_move'))) <= 15:
                    if not self.flag_freq_1_step:
                        self._write_speed_motor(2, freq=10)
                        self.flag_freq_1_step = True

                if 1 < abs(self.set_trav_point - float(self.response.get('traverse_move'))) <= 5:
                    if not self.flag_freq_2_step:
                        self._write_speed_motor(2, freq=8)
                        self.flag_freq_2_step = True

                if abs(self.set_trav_point - float(self.response.get('traverse_move'))) <= 1:
                    self.model.motor_stop(2)

                    command = {'traverse_freq': 10,
                               'stage': 'wait'}
                    self.model.update_main_dict(command)

                    self.signals.wait_yellow_btn.emit()

            elif stage == 'start_point_amort':
                if 5 < abs(self.set_trav_point - float(self.response.get('traverse_move'))) <= 15:
                    if not self.flag_freq_1_step:
                        self._write_speed_motor(2, freq=10)
                        self.flag_freq_1_step = True

                if 1 < abs(self.set_trav_point - float(self.response.get('traverse_move'))) <= 5:
                    if not self.flag_freq_2_step:
                        self._write_speed_motor(2, freq=8)
                        self.flag_freq_2_step = True

                if abs(self.set_trav_point - float(self.response.get('traverse_move'))) <= 1:
                    self.model.motor_stop(2)

                    command = {'traverse_freq': 10,
                               'stage': 'wait'}
                    self.model.update_main_dict(command)

                    if self.response.get('repeat_test', False):
                        self.model.set_regs['repeat_test'] = False
                        self.model.reader_start_test()
                        self._laboratory_test_speed()

                    else:
                        self._test_move_cycle()

            elif stage == 'test_move_cycle':
                if self.count_cycle >= 1:
                    self.model.motor_stop(1)
                    self._pumping_before_test()

            elif stage == 'pumping':
                if self.count_cycle >= 3:
                    self.model.motor_stop(1)

                    if self.response.get('type_test') == 'lab':
                        self._laboratory_test_speed()

                    elif self.response.get('type_test') == 'conv':
                        self._conv_test_speed(1)
                    else:
                        pass

            elif stage == 'test_lab':
                """Лабораторное испытание, крутим до ручной остановки"""
                pass

            elif stage == 'test_conv_speed_one':
                if self.count_cycle >= 6:
                    max_comp = self.response.get('max_comp')
                    max_recoil = self.response.get('max_recoil')
                    self._result_conveyor_test('one', max_comp, max_recoil)
                    if self.response.get('amort').speed_two < 0.03:
                        command = {'stage': 'wait',
                                   'fill_graph': False}
                        self.model.update_main_dict(command)
                        self._stop_gear_end_test()
                    else:
                        self._conv_test_speed(2)

            elif stage == 'test_conv_speed_two':
                if self.count_cycle >= 6:
                    max_comp = self.response.get('max_comp')
                    max_recoil = self.response.get('max_recoil')
                    self._result_conveyor_test('two', max_comp, max_recoil)
                    command = {'stage': 'wait',
                               'fill_graph': False}
                    self.model.update_main_dict(command)
                    self._stop_gear_end_test()

            elif stage == 'stop_gear_end_test':
                move_list = self.response.get('move_list')
                stop_point = reduce(lambda x, y: round(abs(abs(x) - abs(y)), 3), move_list)

                if stop_point < 0.1 or stop_point == move_list[0]:  # Перемещение перестало изменяться
                    self.count_wait_point += 1

                else:
                    self.count_wait_point = 0

                if self.count_wait_point > 3:
                    self.model.set_regs['stage'] = 'wait'
                    self.count_wait_point = 0
                    self._stop_gear_min_pos()

            elif stage == 'stop_gear_min_pos':
                if self.response.get('move') < self.model.main_min_point + 4:
                    self.model.motor_stop(1)
                    time.sleep(0.1)

                    command = {'stage': 'wait',
                               'force_accum_list': [],
                               'move_accum_list': [],
                               'start_pos': False,
                               'start_direction': False,
                               'min_pos': False,
                               'max_pos': False,
                               'test_flag': False,
                               }

                    self.model.update_main_dict(command)

                    if self.response.get('search_hod', False):
                        self.model.set_regs['search_hod'] = False
                        self.signals.search_hod.emit()

                    else:
                        if self.response.get('test_launch', False) is True:
                            self._traverse_install_point('install')
                        else:
                            self._traverse_install_point('stop_test')

            elif stage == 'stop_test':
                if 5 < abs(self.set_trav_point - self.response.get('traverse_move')) <= 15:
                    if not self.flag_freq_1_step:
                        self._write_speed_motor(2, freq=10)
                        self.flag_freq_1_step = True

                if 1 < abs(self.set_trav_point - float(self.response.get('traverse_move'))) <= 5:
                    if not self.flag_freq_2_step:
                        self._write_speed_motor(2, freq=8)
                        self.flag_freq_2_step = True

                if abs(self.set_trav_point - self.response.get('traverse_move')) <= 1:
                    self.model.motor_stop(2)

                    if not self.response.get('alarm_flag', False):
                        self.signals.cancel_test.emit()

                    command = {'stage': 'wait',
                               'traverse_freq': 10}

                    self.model.update_main_dict(command)

            else:
                pass

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_update_stage_on_timer - {e}')

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
            self._write_speed_motor(2, freq=10)
            self.model.set_regs['stage'] = 'alarm_traverse'
            if pos == 'up':
                self.model.motor_down(2)

            elif pos == 'down':
                self.model.motor_up(2)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/move_traverse_out_alarm - {e}')

    def _control_alarm_state(self):
        try:
            if self.response.get('lost_control', False) is True:
                self._lost_control()
            if self.response.get('excess_force', False) is True:
                self._excess_force()
            if self.response.get('safety_fence', False) is True:
                self._safety_fence()
            if self.response.get('max_temperature', 0) >= self.response.get('amort').max_temper:
                self._excess_temperature()

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
        time.sleep(0.1)

        self.model.write_bit_red_light(1)

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
        time.sleep(0.1)

        self.model.write_bit_red_light(1)

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
        time.sleep(0.1)

        self.model.log_error(f'safety fence')
        self.signals.control_msg.emit('safety_fence')

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

        command = {'stage': 'wait',
                   'alarm_flag': True,
                   'alarm_tag': f'alarm_traverse_{pos}',
                   'test_launch': False,
                   'test_flag': False}
        self.model.update_main_dict(command)

        self.model.reader_stop_test()
        time.sleep(0.1)

        self.model.log_error(f'alarm traverse {pos}')
        self.signals.control_msg.emit(f'alarm_traverse_{pos}')

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
            time.sleep(0.1)

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
                               'move_graph': [],
                               'min_pos': False,
                               'max_pos': False,
                               'start_pos': False,
                               'start_direction': False}
                    self.model.update_main_dict(command)
                    self.model.reset_min_point()

                    # if self.response.get('lost_control'):
                    #     self.model.write_bit_unblock_control()

                    # if self.response.get('excess_force'):
                    #     self.model.write_bit_emergency_force()

                    # self.model.write_bit_force_cycle(1)

                    self._traverse_install_point('start_test')

                else:
                    self.model.set_regs['test_flag'] = False
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
            # if self.response.get('excess_force', False) is True:
            #     self.model.write_bit_emergency_force()

            # if self.response.get('lost_control', False) is True:
            #     self.model.write_bit_unblock_control()

            self.lamp_all_switch_off()

            command = {'test_launch': True,
                       'test_flag': False,
                       'fill_graph': False,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'force_graph': [],
                       'move_graph': [],
                       'start_pos': False,
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       }

            self.model.update_main_dict(command)
            self.model.reset_min_point()

            force = self._calc_excess_force()
            self.model.write_emergency_force(force)

            # self.model.write_bit_force_cycle(1)

            if self.response.get('traverse_move', 0) < 10:
                self._traverse_referent_point()

            else:
                self._traverse_install_point('install')

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
                       'start_pos': False,
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
            command = {'stage': 'wait',
                       'search_hod': True,
                       'test_launch': False,
                       'test_flag': False,
                       'fill_graph': False,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       'start_pos': False,
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       }

            self.model.update_main_dict(command)

            self._move_detection()

            self._write_speed_motor(1, speed=0.05)

            self.count_cycle = 0

            # self.model.write_bit_force_cycle(1)

            self.model.reader_start_test()

            self.model.set_regs['stage'] = 'search_hod'

            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/search_hod_gear - {e}')

    def move_gear_set_pos(self):
        try:
            command = {'stage': 'wait',
                       'search_hod': False,
                       'test_launch': False,
                       'test_flag': False,
                       'fill_graph': False,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       'start_pos': False,
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       }
            self.model.update_main_dict(command)

            self._gear_set_pos()

            self._write_speed_motor(1, speed=0.03)

            self.count_cycle = 0

            self.model.reader_start_test()

            self.model.set_regs['stage'] = 'pos_set_gear'

            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/move_gear_set_pos - {e}')

    def _convert_adapter(self, name: str):
        """Перевод номера адаптера в его длинну"""
        try:
            if name == '069' or name == '069-01':
                return 25

            elif name == '069-02' or name == '069-03' or name == '069-04':
                return 34

            elif name == '072':
                return 41

            else:
                return 0

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_convert_adapter - {e}')

    def _traverse_move_position(self, set_point):
        """Непосредственно включение и перемещение траверсы"""
        try:
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self._write_speed_motor(2, freq=20)
            self.model.set_regs['traverse_freq'] = 20
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

    def _traverse_install_point(self, tag):
        """Позционирование траверсы"""
        try:
            amort = self.response.get('amort')
            stock_point = self.response.get('traverse_stock')
            hod = amort.hod
            len_min = amort.min_length
            len_max = amort.max_length
            mid_point = (len_max - len_min) / 2
            adapter = self._convert_adapter(amort.adapter)

            if tag == 'install':
                install_point = int((stock_point + hod / 2) - len_max - adapter)
                self._position_traverse()
                pos_trav = float(self.response.get('traverse_move'))
                if abs(pos_trav - install_point) < 2:
                    self.signals.wait_yellow_btn.emit()

                else:
                    self.model.set_regs['stage'] = 'install_amort'
                    self._traverse_move_position(install_point)

            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self._position_traverse()
                self.model.set_regs['stage'] = 'start_point_amort'
                self._traverse_move_position(start_point)

            elif tag == 'stop_test':
                if not self.response.get('alarm_flag', False):
                    self._position_traverse()

                end_point = int((stock_point + hod / 2) - len_max - adapter)

                self.model.set_regs['stage'] = 'stop_test'
                self._traverse_move_position(end_point)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_traverse_install_point - {e}')

    def _test_move_cycle(self):
        """Проверочный ход"""
        try:
            self._move_detection()

            self._write_speed_motor(1, speed=0.05)

            self.model.set_regs['stage'] = 'test_move_cycle'

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
            
            self._write_speed_motor(1, speed=0.05)

            command = {'stage': 'pumping',
                       'gear_speed': 0.1,
                       }
            self.model.update_main_dict(command)
            self.count_cycle = 0
            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_pumping_before_test - {e}')

    def _conv_test_speed(self, ind):
        """Сигнал на окно конвейерного испытания, разгон до скорости индекса(1 или 2)"""
        try:
            self.signals.conv_win_test.emit()
            amort = self.response.get('amort')

            if ind == 1:
                self._write_speed_motor(1, speed=amort.speed_one)

                command = {'gear_speed': amort.speed_one,
                           'stage': 'test_conv_speed_one',
                           'force_accum_list': [],
                           'move_accum_list': [],
                           'fill_graph': True,
                           }
                self.model.update_main_dict(command)

                self.model.motor_up(1)

            elif ind == 2:
                command = {'gear_speed': amort.speed_one,
                           'stage': 'test_conv_speed_two',
                           }
                self.model.update_main_dict(command)

                self._write_speed_motor(1, speed=amort.speed_two)

            self.count_cycle = 0

        except Exception as e:
            self.model.log_error(f'ERROR in controller/conv_test - {e}')

    def _laboratory_test_speed(self):
        """Сигнал на окно лабораторного испытания, разгон до заданной скорости"""
        try:
            self.signals.lab_win_test.emit()

            amort = self.response.get('amort')
            speed = amort.speed_one
            command = {'stage': 'test_lab',
                       'gear_speed': speed,
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            self._write_speed_motor(1, speed=speed)

            self.count_cycle = 0

            self.model.motor_up(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/start_laboratory_test - {e}')

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
                self.model.write_bit_green_light(1)

            else:
                self.model.write_bit_red_light(1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_result_conveyor_test - {e}')

    def _stop_gear_end_test(self):
        """Остановка двигателя после испытания и перед исходным положением"""
        try:
            self.model.motor_stop(1)

            self.model.set_regs['stage'] = 'stop_gear_end_test'

        except Exception as e:
            self.model.log_error(f'ERROR in controller/_stop_gear_end_test - {e}')

    def _stop_gear_min_pos(self):
        """Снижение скорости и остановка привода в нижней точке"""
        try:
            self.model.reader_stop_test()
            time.sleep(0.2)

            self._write_speed_motor(1, speed=0.03)

            self.model.motor_up(1)

            command = {'stage': 'stop_gear_min_pos',
                       'gear_speed': 0.03,
                       }
            self.model.update_main_dict(command)

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
