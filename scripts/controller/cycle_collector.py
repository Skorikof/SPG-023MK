import numpy as np
import time
from collections import deque
from enum import Enum

from scripts.logger import my_logger
from scripts.controller.stop_detector import StopDetector


class PhaseState(Enum):
    ACCEL = 0
    RUN = 1
    DONE = 2
    ERROR = 3


class Mode(Enum):
    DETECT_ONLY = 0
    COLLECT = 1
    STROKE_ONLY = 2


class CycleCollector:

    def __init__(
        self,
        sample_rate=1000,
        min_halfcycle_fraction=0.2,
        period_stability_threshold=0.02,
        min_stable_cycles=2,

        watchdog_cycles_factor=3.5,
        watchdog_min_sec=0.5,
        watchdog_max_sec=10.0,
    ):

        self.logger = my_logger.get_logger(__name__)
        
        self.stop_detector = StopDetector(
            vel_threshold_getter=lambda: self.vel_threshold,
            stop_ratio=0.05,
            confirm_time_sec=0.25, # Если ложные срабатывния увеличить, если медленно реагирует - уменьшить
        )

        # -------- параметры --------
        self.sample_rate = sample_rate
        self.min_halfcycle_points = int(sample_rate * min_halfcycle_fraction)

        self.period_stability_threshold = period_stability_threshold
        self.min_stable_cycles = min_stable_cycles

        # -------- watchdog --------
        self.watchdog_cycles_factor = watchdog_cycles_factor
        self.watchdog_min_sec = watchdog_min_sec
        self.watchdog_max_sec = watchdog_max_sec
        self.watchdog_timeout_sec = watchdog_max_sec

        self.last_turn_time = None

        # -------- состояния --------
        self.phase_state = PhaseState.ACCEL

        # -------- программа --------
        self.program = []
        self.program_index = 0
        self.program_cycle_counter = 0

        # -------- поток --------
        self.prev_pos = None
        self.prev_sign = 0

        self.turn_count = 0
        self.points_after_turn = 0
        
        self.cycle_min_pos = float("inf")
        self.cycle_max_pos = float("-inf")

        self.current_pos = []
        self.current_force = []

        self.cycles = []

        # -------- скорость --------
        self.vel_hist = deque(maxlen=7)
        self.vel_threshold = 0.0

        # -------- стабильность периода --------
        self.cycle_times = deque(maxlen=5)
        self.last_cycle_time = None

    def load_program(self, program):
        try:
            self.reset()
            self.program = program
            
        except Exception as e:
            self.logger.error(e)

    def _current_program_step(self):
        try:
            if self.program_index >= len(self.program):
                return None
            return self.program[self.program_index]
        
        except Exception as e:
            self.logger.error(e)

    def _update_threshold(self, v):
        try:
            self.vel_hist.append(abs(v))

            if len(self.vel_hist) >= 5:
                noise = np.median(self.vel_hist)
                self.vel_threshold = max(noise * 3, 1e-6)
                
        except Exception as e:
            self.logger.error(e)

    def _sign(self, v):
        try:
            if abs(v) < self.vel_threshold:
                return 0
            return 1 if v > 0 else -1
        
        except Exception as e:
            self.logger.error(e)

    def _is_period_stable(self):
        try:
            if len(self.cycle_times) < self.min_stable_cycles:
                return False

            arr = np.array(self.cycle_times)
            mean = np.mean(arr)
            if mean < 1e-9:
                return False
            
            return np.std(arr) / mean < self.period_stability_threshold
        
        except Exception as e:
            self.logger.error(e)

    def _update_watchdog_timeout(self):
        try:
            if len(self.cycle_times) == 0:
                return

            mean_period = np.mean(self.cycle_times)

            timeout = mean_period * self.watchdog_cycles_factor
            timeout = max(timeout, self.watchdog_min_sec)
            timeout = min(timeout, self.watchdog_max_sec)

            self.watchdog_timeout_sec = timeout
            
        except Exception as e:
            self.logger.error(e)
            
    def _normalize_cycle(self, pos_arr, force_arr):
        if len(pos_arr) == 0:
            return pos_arr, force_arr

        start_idx = np.argmin(pos_arr)

        pos_arr = np.roll(pos_arr, -start_idx)
        force_arr = np.roll(force_arr, -start_idx)

        return pos_arr, force_arr

    def add_stream_dict(self, data):
        try:
            if self.phase_state in (PhaseState.DONE, PhaseState.ERROR):
                return self.phase_state
            
            now = time.perf_counter()

            # # -------- watchdog --------
            # if self.last_turn_time is not None:
            #     if now - self.last_turn_time > self.watchdog_timeout_sec:
            #         self.logger.warning("Watchdog timeout: motion stopped")
            #         self.phase_state = PhaseState.ERROR
            #         return self.phase_state

            pos_arr = data.get("move")
            force_arr = data.get("force")

            if pos_arr is None or force_arr is None:
                return self.phase_state

            for pos, force in zip(pos_arr, force_arr):

                if self.prev_pos is None:
                    self.prev_pos = pos
                    continue

                v = pos - self.prev_pos
                self._update_threshold(v)
                
                self.stop_detector.update(v, self.phase_state, now)

                sign = self._sign(v)
                self.points_after_turn += 1

                if sign != 0 and self.prev_sign != 0 and sign != self.prev_sign:

                    if self.points_after_turn > self.min_halfcycle_points:

                        self.turn_count += 1
                        self.points_after_turn = 0

                        self.last_turn_time = time.perf_counter()

                        if self.turn_count % 2 == 0:

                            now_cycle = time.perf_counter()

                            if self.last_cycle_time is not None:
                                self.cycle_times.append(now_cycle - self.last_cycle_time)

                            self.last_cycle_time = now_cycle

                            # -------- ACCEL --------
                            if self.phase_state == PhaseState.ACCEL:

                                if self._is_period_stable():
                                    self.phase_state = PhaseState.RUN
                                    # self._update_watchdog_timeout()

                                    self.current_pos.clear()
                                    self.current_force.clear()
                                    
                                    self.cycle_min_pos = float("inf")
                                    self.cycle_max_pos = float("-inf")

                            # -------- RUN --------
                            elif self.phase_state == PhaseState.RUN:

                                # self._update_watchdog_timeout()

                                step = self._current_program_step()

                                if step is None:
                                    self.phase_state = PhaseState.DONE
                                    return self.phase_state

                                mode, target_cycles = step

                                if mode == Mode.COLLECT:
                                    pos_np = np.array(self.current_pos, dtype=np.float32)
                                    force_np = np.array(self.current_force, dtype=np.float32)
                                    pos_np, force_np = self._normalize_cycle(pos_np, force_np)
                                    self.cycles.append((pos_np, force_np))

                                elif mode == Mode.STROKE_ONLY:
                                    if self.cycle_min_pos is not None:
                                        stroke = self.cycle_max_pos - self.cycle_min_pos
                                        self.cycles.append((
                                            self.cycle_min_pos,
                                            self.cycle_max_pos,
                                            stroke
                                        ))

                                self.program_cycle_counter += 1

                                if self.program_cycle_counter >= target_cycles:
                                    self.program_index += 1
                                    self.program_cycle_counter = 0

                                    if self.program_index >= len(self.program):
                                        self.phase_state = PhaseState.DONE
                                        return self.phase_state

                            self.current_pos.clear()
                            self.current_force.clear()
                            
                            self.cycle_min_pos = float("inf")
                            self.cycle_max_pos = float("-inf")

                if sign != 0:
                    self.prev_sign = sign
                    
                if self.phase_state == PhaseState.RUN:
                    step = self._current_program_step()
                    mode, _ = step

                    if mode == Mode.COLLECT:
                        self.current_pos.append(pos)
                        self.current_force.append(force)

                    elif mode == Mode.STROKE_ONLY:
                        self.cycle_min_pos = min(self.cycle_min_pos, pos)
                        self.cycle_max_pos = max(self.cycle_max_pos, pos)

                self.prev_pos = pos
        
        except Exception as e:
            self.logger.error(e)
            self.phase_state = PhaseState.ERROR
            
        finally:
            return self.phase_state
            
    def get_cycles(self):
        return list(self.cycles)
    
    def motor_stopped(self):
        return self.stop_detector.stopped

    def reset(self):
        try:
            self.phase_state = PhaseState.ACCEL
            
            self.stop_detector.reset()

            self.program_index = 0
            self.program_cycle_counter = 0

            self.prev_pos = None
            self.prev_sign = 0

            self.turn_count = 0
            self.points_after_turn = 0

            self.current_pos.clear()
            self.current_force.clear()
            
            self.cycle_min_pos = float("inf")
            self.cycle_max_pos = float("-inf")

            self.cycles.clear()

            self.vel_hist.clear()
            self.vel_threshold = 0.0

            self.cycle_times.clear()
            self.last_cycle_time = None

            self.last_turn_time = None
            self.watchdog_timeout_sec = self.watchdog_max_sec
            
        except Exception as e:
            self.logger.error(e)
