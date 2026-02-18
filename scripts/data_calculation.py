import statistics
import numpy as np
from struct import pack

from scripts.logger import my_logger


class CalcData:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        
    def _normalize_cycle(self, x, y, target_len=200):
        try:
            t_old = np.linspace(0, 1, len(x))
            t_new = np.linspace(0, 1, target_len)

            x_new = np.interp(t_new, t_old, x)
            y_new = np.interp(t_new, t_old, y)

            return x_new, y_new
        
        except Exception as e:
            self.logger.error(e)

    def average_cycles(self, cycles, target_len=200):
        try:
            if not cycles:
                return None, None

            xs = []
            ys = []

            for pos, force in cycles:
                x_n, y_n = self._normalize_cycle(pos, force, target_len)
                xs.append(x_n)
                ys.append(y_n)

            mean_x = np.mean(xs, axis=0)
            mean_y = np.mean(ys, axis=0)

            return mean_x, mean_y

        except Exception as e:
            self.logger.error(e)

    def max_speed(self, hod, freq=119):
        """Расчёт максимальной скорости от хода поршня"""
        try:
            koef = round((2 * 17.99) / (2 * 3.1415 * 0.98), 5)
            radius = round((hod / 1000) / 2, 3)
            return round((freq * radius) / koef, 3)

        except Exception as e:
            self.logger.error(e)

    def emergency_force(self, value):
        """Конвертация задаваемого максимального усилия"""
        try:
            arr = []
            val = pack('>f', value)
            for i in range(0, 4, 2):
                arr.append(int((hex(val[i])[2:] + hex(val[i + 1])[2:]), 16))

            return arr

        except Exception as e:
            self.logger.error(e)

    def check_temperature(self, temp_buf: float, max_temper: float):
        """Фиксация максимальной температуры"""
        try:
            if temp_buf > max_temper:
                return temp_buf
            else:
                return max_temper

        except Exception as e:
            self.logger.error(e)

    def middle_min_and_max_force(self, force: list):
        """Усреднение максимального и инимального усилия"""
        try:
            max_rec = max(force)
            max_comp = abs(min(force))
            # if force != []:
            #     rec_ind = force.index(max(force))
            #     max_rec = round(statistics.fmean(force[rec_ind - 5:rec_ind + 5]), 1)

            #     comp_ind = force.index(min(force))
            #     max_comp = round(statistics.fmean(force[comp_ind - 5:comp_ind + 5]), 1)
            
            # else:
            #     max_rec = max_comp = 0

        except Exception as e:
            max_rec = max_comp = 0
            self.logger.error(e)
            
        finally:
            return max_rec, max_comp

    def offset_move_by_hod(self, amort, min_p):
        """Смещение хода на графике от хода поршня"""
        try:
            return round((float(amort.max_length) - float(amort.min_length) - float(amort.hod)) / 2 + min_p, 1)

        except Exception as e:
            self.logger.error(e)

    def power_amort(self, move, force):
        """Расчёт мощности"""
        try:
            temp = 0
            for i in range(1, len(move)):
                step = abs(abs(move[i]) - abs(move[i - 1]))
                
                if step > 0:
                    temp = round(temp + step * abs(force[i - 1]), 1)

            return round((temp * 0.009807) / 1000, 3)

        except Exception as e:
            self.logger.error(e)

    def freq_piston_amort(self, speed, hod):
        """Частота поршня"""
        try:
            return round(speed / (int(hod) * 0.002 * 3.14), 3)

        except Exception as e:
            self.logger.error(e)

    def excess_force(self, amort):
        """Максимально допустимое усилие по усилию аморта"""
        try:
            force = int(max(amort.max_comp, amort.max_recoil) * 5)
            if force >= 1900:
                return 1900
            else:
                return 1500

        except Exception as e:
            self.logger.error(e)

    def calc_dynamic_push_force(self, force, move, static):
        """Расчёт динамической выталкивающей силы"""
        try:
            force_min = force[move.index(min(move))]
            force_max = force[move.index(max(move))]
            force_mid = (force_min + force_max) / 2
            dynamic = round((force_mid - static) / 2 + static, 2)
            
            return dynamic
        
        except Exception as e:
            self.logger.error(e)
            
    def choice_push_force(self, flag, force, move, static):
        """Выбор выталкивающей силы для расчётов и архива"""
        try:
            if flag:
                return self.calc_dynamic_push_force(force, move, static)

            else:
                dynamic = 0
                return static, dynamic

        except Exception as e:
            self.logger.error(e)
            
    def full_circle_done(self):
        try:
            self.logger.debug('Full circle is done')
            if self.flag_fill_graph:
                # offset_p = self.calc_data.offset_move_by_hod(self.data_test.amort, self.min_point)
                
                self.force = [round(x * (-1), 2) for x in self.force_list]
                # self.move = [round(x + offset_p, 2) for x in self.move_list]
                self.move = self.move_list[:]

                max_recoil, max_comp = self.calc_data.middle_min_and_max_force(self.force)
                self.logger.debug(f'Clear recoil --> {max_recoil}, clear comp --> {max_comp}')
                
                push_force = self._choice_push_force()
                self.max_recoil = round(max_recoil + push_force, 1)
                self.max_comp = round(max_comp - push_force, 1)
                self.logger.debug(f'Correct recoil --> {self.max_recoil}, correct comp --> {self.max_comp}')

                self.power_amort = self.calc_data.power_amort(self.force, self.move)
                self.freq_piston = self.calc_data.freq_piston_amort(self.data_test.speed_test, self.data_test.amort.hod)
                
                self.logger.debug('Full circle response parsing is done')

                self.signals.update_data_graph.emit()

            self.signals.full_cycle_count.emit('+1')

        except Exception as e:
            self.logger.error(e)
            
        finally:
            self.min_pos = False
            self.max_pos = False
