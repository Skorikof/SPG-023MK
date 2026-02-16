import numpy as np
from collections import deque

from scripts.logger import my_logger


class CycleCollector:
    def __init__(self,
                 sample_rate=1000,
                 target_cycles=3):
        
        self.logger = my_logger.get_logger(__name__)

        self.sample_rate = sample_rate
        self.target_cycles = target_cycles

        self.prev_pos = None

        self.vel_hist = deque(maxlen=7)
        self.prev_sign = 0

        self.turn_count = 0
        self.points_after_turn = 0

        self.current_pos = []
        self.current_force = []

        self.cycles = []

        # адаптивные параметры
        self.vel_threshold = 0.0
        self.min_halfcycle_points = int(0.2 * sample_rate)

    # --- авто настройка порога ---
    def _update_threshold(self, v):
        try:
            self.vel_hist.append(abs(v))

            if len(self.vel_hist) >= 5:
                noise_level = np.median(self.vel_hist)
                self.vel_threshold = max(noise_level * 3, 1e-6)
        except Exception as e:
            self.logger.error(e)

    def _sign(self, v):
        try:
            if abs(v) < self.vel_threshold:
                return 0
            return 1 if v > 0 else -1
        except Exception as e:
            self.logger.error(e)

    def add_stream_dict(self, data):
        try:
            pos_arr = data.get('move')
            force_arr = data.get('force')

            for pos, force in zip(pos_arr, force_arr):

                if self.prev_pos is None:
                    self.prev_pos = pos
                    self.current_pos.append(pos)
                    self.current_force.append(force)
                    continue

                v = pos - self.prev_pos
                self._update_threshold(v)

                sign = self._sign(v)
                self.points_after_turn += 1

                if sign != 0 and self.prev_sign != 0 and sign != self.prev_sign:

                    if self.points_after_turn > self.min_halfcycle_points:

                        self.turn_count += 1
                        self.points_after_turn = 0

                        if self.turn_count % 2 == 0:

                            self.cycles.append((
                                np.array(self.current_pos),
                                np.array(self.current_force)
                            ))

                            self.current_pos = []
                            self.current_force = []

                if sign != 0:
                    self.prev_sign = sign

                self.current_pos.append(pos)
                self.current_force.append(force)

                self.prev_pos = pos

            return len(self.cycles) >= self.target_cycles
        
        except Exception as e:
            self.logger.error(e)

    def average_cycles(self, cycles, points=1500):
        """Усреднение"""
        try:
            all_pos = np.concatenate([c[0] for c in cycles])
            grid = np.linspace(all_pos.min(), all_pos.max(), points)

            forces = []

            for pos, force in cycles:
                forces.append(np.interp(grid, pos, force))

            return grid, np.mean(forces, axis=0)
        
        except Exception as e:
            self.logger.error(e)
