import numpy as np
import functools
import time
from collections import deque
from enum import Enum

from scripts.logger import my_logger


class StopDetector:
    def __init__(self, vel_threshold=0.02, confirm_time=0.5):
        self.vel_threshold = vel_threshold
        self.confirm_time = confirm_time
        self.below_since = None
        self.stopped = False

    def update(self, velocity, now):
        if abs(velocity) < self.vel_threshold:
            if self.below_since is None:
                self.below_since = now
            elif (now - self.below_since) >= self.confirm_time:
                self.stopped = True
        else:
            self.below_since = None
            self.stopped = False

    def is_stopped(self):
        return self.stopped
    
    def reset(self):
        self.below_since = None
        self.stopped = False


class PhaseState(Enum):
    ACCEL = 0
    RUN = 1
    DONE = 2
    ERROR = 3


class Mode(Enum):
    DETECT_ONLY = 0
    COLLECT = 1
    STROKE_ONLY = 2
    WAIT_STOP = 3


class CycleCollector:
    def __init__(
        self,
        sample_rate=1000,
        min_halfcycle_fraction=0.2,
        period_stability_threshold=0.02,
        min_stable_cycles=2,
        ):
        self.logger = my_logger.get_logger(__name__)
        self.stop_detector = StopDetector()

        # -------- параметры --------
        self.sample_rate = sample_rate
        self.min_halfcycle_points = int(sample_rate * min_halfcycle_fraction)
        self.period_stability_threshold = period_stability_threshold
        self.min_stable_cycles = min_stable_cycles

        # -------- состояния --------
        self.active = False
        self.phase_state = PhaseState.ACCEL
        self.cycle_completed = False
        self.skip_accel = False
        self.cycle_callback = None
        self.last_completed_step = None
        self.last_step_result = None

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
    
    @staticmethod
    def log_exceptions(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception:
                self.logger.exception(f"ERROR in {func.__name__}")
                self.phase_state = PhaseState.ERROR
                self.active = False
                return self.phase_state
        return wrapper
    
    @log_exceptions
    def load_program(self, program, skip_accel=False):
        self.reset()
        self.program = program
        self.skip_accel = skip_accel

        if self.skip_accel:
            self.phase_state = PhaseState.RUN
        
        self.active = True

    @log_exceptions
    def _current_program_step(self):
        if self.program_index >= len(self.program):
            return None
        return self.program[self.program_index]

    @log_exceptions
    def _update_threshold(self, v):
        self.vel_hist.append(abs(v))
        if len(self.vel_hist) >= 5:
            noise = np.median(self.vel_hist)
            self.vel_threshold = max(noise * 3, 1e-6)

    @log_exceptions
    def _sign(self, v):
        if abs(v) < self.vel_threshold:
            return 0
        return 1 if v > 0 else -1

    @log_exceptions
    def _is_period_stable(self):
        if len(self.cycle_times) < self.min_stable_cycles:
            return False
        arr = np.array(self.cycle_times)
        mean = np.mean(arr)
        if mean < 1e-9:
            return False
        return np.std(arr) / mean < self.period_stability_threshold
    
    @log_exceptions
    def _normalize_cycle(self, pos_arr, force_arr):
        if len(pos_arr) == 0:
            return pos_arr, force_arr
        start_idx = np.argmin(pos_arr)
        pos_arr = np.roll(pos_arr, -start_idx)
        force_arr = np.roll(force_arr, -start_idx)
        return pos_arr, force_arr
    
    @log_exceptions
    def add_stream_dict(self, data):
        if not self.active:
            return self.phase_state
        if self.phase_state in (PhaseState.DONE, PhaseState.ERROR):
            return self.phase_state
        pos_arr = data.get("move")
        force_arr = data.get("force")
        if pos_arr is None or force_arr is None:
            return self.phase_state
        
        base = time.perf_counter()
        dt = 1.0 / float(self.sample_rate)
        for i, (pos, force) in enumerate(zip(pos_arr, force_arr)):
            now = base + i * dt
            self._process_sample(pos, force, now)
            if self.phase_state in (PhaseState.DONE, PhaseState.ERROR):
                break
        return self.phase_state
    
    @log_exceptions
    def _process_sample(self, pos, force, now):
        if self.prev_pos is None:
            self.prev_pos = pos
            return
        v = (pos - self.prev_pos) * float(self.sample_rate)
        self._update_threshold(v)
        self.stop_detector.update(v, now)
        sign = self._sign(v)
        self.points_after_turn += 1
        turn_detected = self._detect_turn(sign)
        if turn_detected:
            self._process_turn()
        self._append_data_if_needed(pos, force)
        if sign != 0:
            self.prev_sign = sign
        self.prev_pos = pos
        
    @log_exceptions
    def _detect_turn(self, sign):
        if sign != 0 and self.prev_sign != 0 and sign != self.prev_sign:
            if self.points_after_turn > self.min_halfcycle_points:
                self.points_after_turn = 0
                self.turn_count += 1
                return True
        return False
    
    @log_exceptions
    def _process_turn(self):
        if self.turn_count % 2 != 0:
            return  # только полный цикл
        now_cycle = time.perf_counter()
        if self.last_cycle_time is not None:
            self.cycle_times.append(now_cycle - self.last_cycle_time)
        self.last_cycle_time = now_cycle
        if self.phase_state == PhaseState.ACCEL:
            self._handle_accel_phase()
        elif self.phase_state == PhaseState.RUN:
            self._handle_run_phase()
    
    @log_exceptions
    def _handle_accel_phase(self):
        if self._is_period_stable():
            self.phase_state = PhaseState.RUN
            self._reset_cycle_buffers()
    
    @log_exceptions
    def _handle_run_phase(self):
        step = self._current_program_step()
        if step is None:
            self.phase_state = PhaseState.DONE
            self.active = False
            return
        mode, target_cycles = step
        cycle_completed = self._execute_mode(mode)
        if cycle_completed:
            self._advance_program_if_needed(target_cycles)
    
    @log_exceptions
    def _execute_mode(self, mode):
        if mode == Mode.DETECT_ONLY:
            return self._handle_detect_only()
        if mode == Mode.COLLECT:
            return self._handle_collect()
        if mode == Mode.STROKE_ONLY:
            return self._handle_stroke()
        if mode == Mode.WAIT_STOP:
            return self._handle_wait_stop()
        return False

    @log_exceptions
    def _append_data_if_needed(self, pos, force):
        if self.phase_state != PhaseState.RUN:
            return
        step = self._current_program_step()
        if step is None:
            return
        mode, _ = step
        if mode == Mode.COLLECT:
            self.current_pos.append(pos)
            self.current_force.append(force)
        elif mode == Mode.STROKE_ONLY:
            self.cycle_min_pos = min(self.cycle_min_pos, pos)
            self.cycle_max_pos = max(self.cycle_max_pos, pos)
    
    @log_exceptions
    def _reset_cycle_buffers(self):
        self.current_pos.clear()
        self.current_force.clear()
        self.cycle_min_pos = float("inf")
        self.cycle_max_pos = float("-inf")
    
    @log_exceptions
    def _handle_detect_only(self) -> bool:
        """
        Завершает один шаг на каждый полный оборот.
        Никакие данные не сохраняются.
        """
        return True
    
    @log_exceptions
    def _handle_collect(self) -> bool:
        if len(self.current_pos) == 0:
            return False
        pos_np = np.array(self.current_pos, dtype=np.float32)
        force_np = np.array(self.current_force, dtype=np.float32)
        pos_np, force_np = self._normalize_cycle(pos_np, force_np)
        result = (pos_np, force_np)
        if self.cycle_callback:
            self.cycle_callback(result)
        else:
            self.cycles.append(result)
            self.last_step_result = self.cycles.copy()
        self._reset_cycle_buffers()
        return True
    
    @log_exceptions
    def _handle_stroke(self) -> bool:
        if self.cycle_min_pos == float("inf"):
            return False
        result = (
            self.cycle_min_pos,
            self.cycle_max_pos,
            self.cycle_max_pos - self.cycle_min_pos
        )
        self.cycles.append(result)
        self.last_step_result = self.cycles.copy()
        self._reset_cycle_buffers()
        return True
    
    @log_exceptions
    def _handle_wait_stop(self) -> bool:
        """Завершает шаг, когда движение устойчиво остановилось"""
        # StopDetector уже обновляется в _process_sample
        if not self.stop_detector.is_stopped():
            return False
        return True

    @log_exceptions
    def _advance_program_if_needed(self, target_cycles):
        if target_cycles is None:
            return
        self.program_cycle_counter += 1
        if self.program_cycle_counter >= target_cycles:
            self.last_completed_step = self.program[self.program_index]
            self.program_index += 1
            self.program_cycle_counter = 0
            if self.program_index >= len(self.program):
                self.phase_state = PhaseState.DONE
                self.active = False
    
    def reset_active_collate(self):
        self.active = False
        
    def set_cycle_callback(self, callback):
        """Задать функцию, которая будет получать каждый завершённый цикл"""
        self.cycle_callback = callback
        
    def get_last_completed_step(self):
        result = self.last_completed_step
        self.last_completed_step = None
        return result

    def get_last_step_result(self):
        result = self.last_step_result
        self.last_step_result = None
        return result

    def get_cycles(self):
        return list(self.cycles)
    
    def motor_stopped(self):
        return self.stop_detector.stopped

    def reset(self):
        self.active = False
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
        self.last_completed_step = None
        self.last_step_result = None
        self.cycle_completed = False
        self.cycle_callback = None
