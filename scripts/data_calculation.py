import statistics
import numpy as np
from struct import pack

from scripts.logger import my_logger


class CalcData:
    SPEED_CONFIG = {
        (100, float('inf')): {'slow': 0.03, 'medium': 0.1, 'fast': 0.2},
        (50, 100): {'slow': 0.02, 'medium': 0.06, 'fast': 0.1},
        (0, 50): {'slow': 0.01, 'medium': 0.03, 'fast': 0.03},
    }
    
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        
    def definition_speed_by_hod(self, tag: str, hod: int) -> float:
        """Get speed based on hod value and speed tag."""
        try:
            # Find matching range and get speed
            for (min_hod, max_hod), speeds in self.SPEED_CONFIG.items():
                if min_hod < hod <= max_hod:
                    return speeds.get(tag, 0.03)
            
            return 0.03  # Safe default

        except Exception as e:
            self.logger.error(e)
            return 0.03  # Safe default on error
        
    def _normalize_cycle(self, x, y, target_len=1000):
        """
        Интерполирует цикл к заданному количеству точек target_len.
        Тут же в return переворачиваю y_new, пожелания заказчика на такой конечный вид графика
        """
        try:
            t_old = np.linspace(0, 1, len(x))
            t_new = np.linspace(0, 1, target_len)
            x_new = np.interp(t_new, t_old, x)
            y_new = np.interp(t_new, t_old, y)
            return x_new, -y_new
        
        except Exception as e:
            self.logger.error(e)

    def average_cycles(self, cycles, target_len=1000):
        """Усредняет несколько циклов, предварительно нормализуя их длинну"""
        try:
            if not cycles:
                return None, None
            xs = []
            ys = []
            for pos, force in cycles:
                x_n, y_n = self._normalize_cycle(pos, force, target_len)
                xs.append(x_n)
                ys.append(y_n)
                # xs.append(pos)
                # ys.append(force)
            mean_x = np.mean(xs, axis=0)
            mean_y = np.mean(ys, axis=0)
            return mean_x, mean_y

        except Exception as e:
            self.logger.error(e)
            
    def correct_force_with_koef(self, force, koef, offset):
        try:
            return force * koef - offset
            
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
        
    def middle_min_and_max_force_array(self, force: np.array):
        """Вычисление и усреднение максимального и инимального усилия из массива"""
        return np.max(force[1]), abs(min(force[1]))
        
    def offset_move_by_hod(self, amort, min_p):
        """Смещение хода на графике от хода поршня"""
        try:
            return round((float(amort.max_length) - float(amort.min_length) - float(amort.hod)) / 2 + min_p, 1)

        except Exception as e:
            self.logger.error(e)

    def calc_power_amort(self, move, force):
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
            
    def calc_power_amort_array(self, move: np.array, force: np.array):
        """Расчёт мощности из массивов"""
        try:
            steps = np.abs(np.abs(move[1:]) - np.abs(move[:-1]))
            mask = steps > 0
            if not np.any(mask):
                return 0.0
            temp = np.dot(steps[mask], np.abs(force[:-1])[mask])
            return round((temp * 0.009807) / 1000, 3)

        except Exception as e:
            self.logger.error(e)
            return 0.0

    def calc_freq_piston_amort(self, speed, hod):
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
            
    def calc_dynamic_push_force_array(self, move, force, static):
        try:
            force_min = abs(force[np.argmin(move)])
            force_max = abs(force[np.argmax(move)])
            force_avg = (force_min + force_max) / 2
            dynamic = (force_avg + static) / 2
            
            return dynamic
            
        except Exception as e:
            self.logger.error(f"Error calculating dynamic force: {e}")
            return None
