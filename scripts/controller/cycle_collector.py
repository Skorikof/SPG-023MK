import numpy as np
import time
from collections import deque
from enum import Enum

from scripts.logger import my_logger
from .stop_detector import StopDetector


class PhaseState(Enum):
    ACCEL = 0
    RUN = 1
    DONE = 2
    ERROR = 3


class Mode(Enum):
    DETECT_ONLY = 0
    COLLECT = 1
    STROKE_ONLY = 2
    NMT_CAPTURE = 3      # Режим 1: захват позиции НМТ на скорости
    NMT_FINAL = 4        # Режим 2: доворот до НМТ на малой скорости


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
        self.cycle_completed = False
        self.skip_accel = False
        self.cycle_callback = None

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
        
        # -------- Для определения НМТ --------
        self.nmt_detected = False
        self.nmt_captured_pos = None        # Захваченная позиция НМТ
        self.nmt_capture_cycle = None       # Цикл, в котором захватили
        self.nmt_approach_direction = 0     # Направление подхода к НМТ (+1 или -1)
        self.nmt_approach_active = False    # Флаг активного доворота
        self.nmt_capture_result = {
            'position': None,      # позиция НМТ
            'direction_to_nmt': None,  # направление к НМТ (+1 вверх, -1 вниз)
            'current_pos': None,   # текущая позиция при захвате (опционально)
            'timestamp': None      # время захвата
        }
            
    def load_program(self, program, skip_accel=False):
        try:
            self.reset()
            self.program = program
            self.skip_accel = skip_accel

            if self.skip_accel:
                self.phase_state = PhaseState.RUN

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
        if self.phase_state in (PhaseState.DONE, PhaseState.ERROR):
            return self.phase_state
        pos_arr = data.get("move")
        force_arr = data.get("force")
        if pos_arr is None or force_arr is None:
            return self.phase_state
        now = time.perf_counter()
        for pos, force in zip(pos_arr, force_arr):
            self._process_sample(pos, force, now)
            if self.phase_state in (PhaseState.DONE, PhaseState.ERROR):
                break
        return self.phase_state
    
    def _process_sample(self, pos, force, now):
        if self.prev_pos is None:
            self.prev_pos = pos
            return
        v = pos - self.prev_pos
        self._update_threshold(v)
        self.stop_detector.update(v, self.phase_state, now)
        sign = self._sign(v)
        self.points_after_turn += 1
        turn_detected = self._detect_turn(sign)
        if turn_detected:
            self._process_turn(now)
        self._append_data_if_needed(pos, force)
        if sign != 0:
            self.prev_sign = sign
        self.prev_pos = pos
        
    def _detect_turn(self, sign):
        if sign != 0 and self.prev_sign != 0 and sign != self.prev_sign:
            if self.points_after_turn > self.min_halfcycle_points:
                self.points_after_turn = 0
                self.turn_count += 1
                return True
        return False
    
    def _process_turn(self, now):
        self.last_turn_time = now
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
            
    def _handle_accel_phase(self):
        if self._is_period_stable():
            self.phase_state = PhaseState.RUN
            self._reset_cycle_buffers()
            
    def _handle_run_phase(self):
        step = self._current_program_step()
        if step is None:
            self.phase_state = PhaseState.DONE
            return
        mode, target_cycles = step
        cycle_completed = self._execute_mode(mode)
        if cycle_completed:
            self._advance_program_if_needed(target_cycles)
            
    def _execute_mode(self, mode):
        if mode == Mode.COLLECT:
            return self._handle_collect()
        if mode == Mode.STROKE_ONLY:
            return self._handle_stroke()
        if mode == Mode.NMT_CAPTURE:
            return self._handle_nmt_capture()
        if mode == Mode.NMT_FINAL:
            return self._handle_nmt_final()
        return False

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
        
    def _reset_cycle_buffers(self):
        self.current_pos.clear()
        self.current_force.clear()
        self.cycle_min_pos = float("inf")
        self.cycle_max_pos = float("-inf")
        
    def _handle_collect(self) -> bool:
        if len(self.current_pos) == 0:
            return False
        pos_np = np.array(self.current_pos, dtype=np.float32)
        force_np = np.array(self.current_force, dtype=np.float32)
        pos_np, force_np = self._normalize_cycle(pos_np, force_np)
        self.cycles.append((pos_np, force_np))
        if self.cycle_callback is not None:
            self.cycle_callback(pos_np, force_np)
        self._reset_cycle_buffers()
        return True
    
    def _handle_stroke(self) -> bool:
        if self.cycle_min_pos == float("inf"):
            return False
        stroke = self.cycle_max_pos - self.cycle_min_pos
        self.cycles.append((
            self.cycle_min_pos,
            self.cycle_max_pos,
            stroke
        ))
        self._reset_cycle_buffers()
        return True

    def _handle_nmt_capture(self) -> bool:
        current_nmt = (
            self.cycle_min_pos
            if self.cycle_min_pos != float("inf")
            else None
        )
        if current_nmt is None:
            return False
        self.nmt_captured_pos = current_nmt
        direction_to_nmt = -self.prev_sign if self.prev_sign != 0 else 0
        self.nmt_capture_result = {
            'position': current_nmt,
            'direction_to_nmt': direction_to_nmt,
            'current_pos': self.prev_pos,
            'timestamp': time.perf_counter()
        }
        self.logger.info(
            f"NMT captured: pos={current_nmt:.3f}, "
            f"direction to NMT={direction_to_nmt}"
        )
        # переход к следующему шагу
        self.program_index += 1
        self.program_cycle_counter = 0
        self._reset_cycle_buffers()
        return True

    def _handle_nmt_final(self) -> bool:
        if self.nmt_captured_pos is None:
            self.logger.error("NMT_FINAL but no captured position")
            self.phase_state = PhaseState.ERROR
            return False
        target_direction = self.nmt_capture_result.get('direction_to_nmt', 0)
        if target_direction == 0:
            self.logger.error("Invalid direction to NMT")
            self.phase_state = PhaseState.ERROR
            return False
        # активируем режим один раз
        if not self.nmt_approach_active:
            self.nmt_approach_active = True
            self.logger.info(
                f"Starting NMT approach: target={self.nmt_captured_pos:.3f}, "
                f"direction={target_direction}"
            )
        # ---- проверка достижения НМТ выполняется ВСЕГДА ----
        current_sign = self.prev_sign
        current_pos = self.prev_pos
        if target_direction > 0:
            if current_sign > 0 and current_pos >= self.nmt_captured_pos:
                self.nmt_detected = True
        else:
            if current_sign < 0 and current_pos <= self.nmt_captured_pos:
                self.nmt_detected = True
        if self.nmt_detected:
            self.logger.info(f"NMT reached at {current_pos:.3f}")
            self.program_index += 1
            self.program_cycle_counter = 0
            self.nmt_approach_active = False
            return True
        return False
    
    def _advance_program_if_needed(self, target_cycles):
        if target_cycles is None:
            return
        self.program_cycle_counter += 1
        if self.program_cycle_counter >= target_cycles:
            self.program_index += 1
            self.program_cycle_counter = 0
            if self.program_index >= len(self.program):
                self.phase_state = PhaseState.DONE

    def set_cycle_callback(self, callback):
        """Задать функцию, которая будет получать каждый завершённый цикл"""
        self.cycle_callback = callback
            
    def get_cycles(self):
        return list(self.cycles)
    
    def motor_stopped(self):
        return self.stop_detector.stopped
    
    def is_nmt_reached(self):
        """Проверить, достигнута ли целевая НМТ в режиме доворота"""
        return self.nmt_detected

    def get_nmt_target(self):
        """Получить целевую позицию НМТ (для внешнего управления ПЧ)"""
        return self.nmt_captured_pos
    
    def get_nmt_capture_info(self):
        """Получить информацию о захваченной НМТ"""
        if self.nmt_capture_result['position'] is None:
            return None
        return self.nmt_capture_result.copy()

    def get_nmt_direction(self):
        """Получить направление к НМТ (+1 вверх, -1 вниз, 0 неизвестно)"""
        return self.nmt_capture_result.get('direction_to_nmt', 0)

    def get_nmt_position(self):
        """Получить позицию НМТ"""
        return self.nmt_capture_result.get('position', None)

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
            
            self.nmt_detected = False
            self.nmt_captured_pos = None
            self.nmt_capture_cycle = None
            self.nmt_approach_direction = 0
            self.nmt_approach_active = False
            self.nmt_capture_result = {
                'position': None,
                'direction_to_nmt': None,
                'current_pos': None,
                'timestamp': None
            }
            
            self.cycle_completed = False
            self.cycle_callback = None
            
        except Exception as e:
            self.logger.error(e)
