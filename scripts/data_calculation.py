# -*- coding: utf-8 -*-
import numpy as np
from struct import pack

from scripts.logger import my_logger


class CalcData:
    SPEED_CONFIG = {
        (100, float('inf')): {'slow': 0.03, 'medium': 0.1, 'fast': 0.2},
        (50, 100): {'slow': 0.02, 'medium': 0.06, 'fast': 0.1},
        (0, 50): {'slow': 0.02, 'medium': 0.03, 'fast': 0.03},
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
        
    def _interp_force_on_grid(self, x, y, x_grid):
        x = np.asarray(x, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)
        mask = np.isfinite(x) & np.isfinite(y)
        x = x[mask]
        y = y[mask]
        if x.size < 2:
            return None
        order = np.argsort(x)
        x = x[order]
        y = y[order]
        # 0.1 мм — физическая квантовка move (см. parser: -0.1 * value)
        q = np.float32(0.1)
        xq = np.round(x / q) * q
        # медиана силы на каждом квантованном x
        x_u, inv = np.unique(xq, return_inverse=True)
        y_u = np.empty_like(x_u, dtype=np.float32)
        for i in range(x_u.size):
            y_u[i] = np.median(y[inv == i])
        if x_u.size < 2:
            return None
        return np.interp(x_grid, x_u, y_u)
    
    def average_cycles(self, cycles, target_len=1000):
        """
        Усреднение циклов по перемещению (а не по времени):
        - ветвь 1: НМТ->ВМТ (x растёт)
        - ветвь 2: ВМТ->НМТ (x падает)
        """
        try:
            if not cycles:
                return None, None
            # 1) нормализуем длину/знак как раньше, но НЕ усредняем x
            norm = []
            for pos, force in cycles:
                x, y = self._normalize_cycle(pos, force, target_len)
                if x is None or y is None:
                    continue
                norm.append((np.asarray(x), np.asarray(y)))

            if not norm:
                return None, None
            # 2) делим на ветви
            branches_a = []
            branches_b = []
            for x, y in norm:
                imax = int(np.nanargmax(x))
                xa, ya = x[:imax + 1], y[:imax + 1]
                xb, yb = x[imax:], y[imax:]
                # ветвь B приведём к возрастающему x для интерполяции
                xb = xb[::-1]
                yb = yb[::-1]
                branches_a.append((xa, ya))
                branches_b.append((xb, yb))
            # 3) общая область по X (пересечение диапазонов), чтобы не экстраполировать
            def overlap_grid(branches):
                mins = []
                maxs = []
                for x, _ in branches:
                    x = np.asarray(x, dtype=np.float64)
                    x = x[np.isfinite(x)]
                    if x.size:
                        mins.append(np.min(x))
                        maxs.append(np.max(x))
                if not mins:
                    return None
                x_min = max(mins)
                x_max = min(maxs)
                if not np.isfinite(x_min) or not np.isfinite(x_max) or (x_max - x_min) <= 1e-6:
                    return None
                q = 0.1
                # выровнять границы по сетке 0.1 мм
                x_min_q = np.ceil(x_min / q) * q
                x_max_q = np.floor(x_max / q) * q
                if x_max_q - x_min_q < q:
                    return None
                xg = np.arange(x_min_q, x_max_q + 0.5 * q, q, dtype=np.float32)
                if xg.size < 10:
                    return None
                return xg
            # x_grid_a = overlap_grid(branches_a)
            # x_grid_b = overlap_grid(branches_b)
            # if x_grid_a is None or x_grid_b is None:
            x_grid = overlap_grid(branches_a + branches_b)
            if x_grid is None:
                # fallback на старое поведение, если что-то пошло не так
                xs = []
                ys = []
                for x, y in norm:
                    xs.append(x)
                    ys.append(y)
                ref_x = xs[0]
                mean_y = np.mean(ys, axis=0)
                return ref_x, mean_y
            # 4) интерполируем силы на сетку и усредняем
            ya_list = []
            yb_list = []
            # for (xa, ya), (xb, yb) in zip(branches_a, branches_b):
            for i in range(min(len(branches_a), len(branches_b))):
                xa, ya = branches_a[i]
                xb, yb = branches_b[i]
                # ya_i = self._interp_force_on_grid(xa, ya, x_grid_a)
                # yb_i = self._interp_force_on_grid(xb, yb, x_grid_b)
                ya_i = self._interp_force_on_grid(xa, ya, x_grid)
                yb_i = self._interp_force_on_grid(xb, yb, x_grid)
                if ya_i is not None:
                    ya_list.append(ya_i)
                if yb_i is not None:
                    yb_list.append(yb_i)

            if not ya_list or not yb_list:
                return None, None
            mean_ya = np.mean(np.vstack(ya_list), axis=0)
            mean_yb = np.mean(np.vstack(yb_list), axis=0)
            
            # Сведение значений в точках разворота, чтобы не было “ступеньки” при склейке
            # НМТ = начало сетки, ВМТ = конец сетки
            nmt = 0
            vmt = -1
            y_nmt = 0.5 * (mean_ya[nmt] + mean_yb[nmt])
            y_vmt = 0.5 * (mean_ya[vmt] + mean_yb[vmt])
            mean_ya[nmt] = y_nmt
            mean_yb[nmt] = y_nmt
            mean_ya[vmt] = y_vmt
            mean_yb[vmt] = y_vmt
        
            # 5) склеиваем петлю: A (вперёд) + B (назад)
            # x_out = np.concatenate([x_grid_a, x_grid_b[::-1]])
            x_out = np.concatenate([x_grid, x_grid[::-1]])
            y_out = np.concatenate([mean_ya, mean_yb[::-1]])
            
            # Явное замыкание: дубль первой точки в конце
            x_out = np.concatenate([x_out, x_out[:1]])
            y_out = np.concatenate([y_out, y_out[:1]])
        
            return x_out, y_out

        except Exception as e:
            self.logger.error(e)
            return None, None
            
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
        """Вычисление максимального и минимального усилия"""
        if isinstance(force, list):
            return max(force), min(force)
        elif isinstance(force, np.ndarray):
            return np.max(force), np.min(force)

    def calc_power_amort(self, move: list, force: list):
        """Расчёт мощности"""
        try:
            if move is None or force is None or len(move) < 2:
                return 0.0
            # если кривая замкнута явным дублем первой точки — игнорируем её
            if abs(move[-1] - move[0]) < 1e-6 and abs(force[-1] - force[0]) < 1e-6:
                move = move[:-1]
                force = force[:-1]
                
            temp = 0
            for i in range(1, len(move)):
                step = abs(abs(move[i]) - abs(move[i - 1]))
                
                if step > 0:
                    temp = round(temp + step * abs(force[i - 1]), 1)

            return round((temp * 0.009807) / 1000, 3)

        except Exception as e:
            self.logger.error(e)
            
    def calc_power_amort_array(self, move: np.ndarray, force: np.ndarray):
        """Расчёт мощности из массивов"""
        try:
            if move is None or force is None or move.size < 2:
                return 0.0
            # если кривая замкнута явным дублем первой точки — игнорируем её
            if abs(float(move[-1] - move[0])) < 1e-6 and abs(float(force[-1] - force[0])) < 1e-6:
                move = move[:-1]
                force = force[:-1]
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
            
    def calc_dynamic_push_force_array(self, move, force, static):
        try:
            force_min = abs(force[np.argmin(move)])
            force_max = abs(force[np.argmax(move)])
            force_avg = (force_min + force_max) / 2
            dynamic = (force_avg + static) / 2
            
            return round(dynamic, 1)
            
        except Exception as e:
            self.logger.error(f"Error calculating dynamic force: {e}")
            return None
