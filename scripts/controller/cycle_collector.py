# -*- coding: utf-8 -*-
import numpy as np
import functools
import time
from collections import deque
from enum import Enum

from scripts.logger import my_logger


class StopDetector:
    def __init__(self, vel_threshold=0.02, confirm_time=0.5):
        self.min_vel_threshold = float(vel_threshold)
        self.vel_threshold = float(vel_threshold)
        self.confirm_time = confirm_time
        self.below_since = None
        self.stopped = False

    def set_threshold(self, vel_threshold: float):
        """Set current threshold, keeping a minimal floor."""
        try:
            self.vel_threshold = max(float(vel_threshold), self.min_vel_threshold)
        except Exception:
            pass

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
    NMT_CAPTURE = 4
    NMT_FINAL = 5
    MID_FINAL = 6


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
        self.sample_rate = float(sample_rate)
        self.min_halfcycle_fraction = float(min_halfcycle_fraction)
        self.period_stability_threshold = period_stability_threshold
        self.min_stable_cycles = min_stable_cycles

        # -------- оценка реальной частоты буфера --------
        self._current_sample_rate = float(sample_rate)
        self._sr_alpha = 0.15
        self._last_count = None
        self._last_count_ts = None

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

        # -------- потоковое время (по sample_rate) --------
        self.stream_time = None

        # -------- НМТ (нижняя мёртвая точка) --------
        self.nmt_values = deque(maxlen=20)
        self.nmt_estimate = None
        self.nmt_target_pos = None
        self.nmt_tolerance = 0.5
        self.nmt_confirm_points = 3
        self._nmt_in_tol_points = 0
        
        # -------- ВМТ (верхняя мёртвая точка) --------
        self.vmt_values = deque(maxlen=20)
        self.vmt_estimate = None

        # -------- Середина хода (ВМТ->НМТ, первый проход) --------
        self.mid_target_pos = None
        self.mid_tolerance = 1.0
        self.mid_confirm_points = 3
        self._mid_in_tol_points = 0
        self._mid_armed = False
        self._mid_nmt_ref = None
        self._mid_vmt_ref = None

        # -------- экстремумы полупериода (между разворотами) --------
        self.half_min_pos = float("inf")
        self.half_max_pos = float("-inf")
        self._start_pos = None
        
        self.vel_window_points = 5
        self._pos_window = deque(maxlen=self.vel_window_points + 1)

    def set_nmt_target(self, target_pos: float, *, tolerance: float = 0.5, confirm_points: int = 3):
        """Задать целевую НМТ (в тех же единицах, что и `move`)."""
        self.nmt_target_pos = float(target_pos)
        self.nmt_tolerance = float(tolerance)
        self.nmt_confirm_points = max(1, int(confirm_points))
        self._nmt_in_tol_points = 0

    def get_nmt_estimate(self):
        """Оценка НМТ по предыдущим циклам (или None)."""
        return self.nmt_estimate
    
    def get_vmt_estimate(self):
        """Оценка ВМТ по предыдущим циклам (или None)."""
        return self.vmt_estimate

    def _update_nmt_from_cycle_extrema(self):
        """Обновить оценку НМТ по минимуму перемещения в текущем полном цикле."""
        if self.cycle_min_pos == float("inf"):
            return
        try:
            nmt = float(self.cycle_min_pos)
            self.nmt_values.append(nmt)
            arr = np.asarray(self.nmt_values, dtype=np.float32)
            if arr.size:
                self.nmt_estimate = float(np.median(arr))
        except Exception:
            pass
        
    def _update_vmt_from_value(self, vmt_value: float):
        """Обновить оценку ВМТ по значению максимума (обычно на развороте в ВМТ)."""
        try:
            vmt = float(vmt_value)
            self.vmt_values.append(vmt)
            arr = np.asarray(self.vmt_values, dtype=np.float32)
            if arr.size:
                self.vmt_estimate = float(np.median(arr))
        except Exception:
            pass

    def set_mid_params(self, *, tolerance: float = 1.0, confirm_points: int = 2):
        """Настройки для остановки в середине хода (режим MID_FINAL)."""
        self.mid_tolerance = float(tolerance)
        self.mid_confirm_points = max(1, int(confirm_points))
        self._mid_in_tol_points = 0

    def _reset_half_extrema(self, pos):
        try:
            p = float(pos)
        except Exception:
            return
        self.half_min_pos = p
        self.half_max_pos = p
    
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
    def load_program(self, program, skip_accel=False, preserve_nmt: bool = False):
        preserved_nmt_values = None
        preserved_nmt_estimate = None
        preserved_nmt_target = None
        preserved_nmt_cfg = None
        if preserve_nmt:
            preserved_nmt_values = list(self.nmt_values)
            preserved_nmt_estimate = self.nmt_estimate
            preserved_nmt_target = self.nmt_target_pos
            preserved_nmt_cfg = (self.nmt_tolerance, self.nmt_confirm_points)

        self.reset()

        if preserve_nmt and preserved_nmt_values is not None:
            self.nmt_values.extend(preserved_nmt_values)
            self.nmt_estimate = preserved_nmt_estimate
            self.nmt_target_pos = preserved_nmt_target
            if preserved_nmt_cfg is not None:
                self.nmt_tolerance, self.nmt_confirm_points = preserved_nmt_cfg

        self.program = program
        self.skip_accel = skip_accel

        if self.skip_accel:
            self.phase_state = PhaseState.RUN
        
        self.active = True

    def set_nmt_params(self, *, tolerance: float = 1.0, confirm_points: int = 2):
        """Настройки для доворота до НМТ без задания явной цели."""
        self.nmt_tolerance = float(tolerance)
        self.nmt_confirm_points = max(1, int(confirm_points))
        self._nmt_in_tol_points = 0

    def clear_nmt(self):
        """Сбросить сохранённую НМТ (оценку и историю)."""
        self.nmt_values.clear()
        self.nmt_estimate = None
        self.nmt_target_pos = None
        self._nmt_in_tol_points = 0

    @log_exceptions
    def _current_program_step(self):
        if self.program_index >= len(self.program):
            return None
        return self.program[self.program_index]

    @log_exceptions
    def _update_threshold(self, v):
        self.vel_hist.append(abs(v))
        if len(self.vel_hist) >= 5:
            arr = np.sort(np.asarray(self.vel_hist, dtype=np.float32))
            k = min(3, arr.size)
            noise_floor = float(np.median(arr[:k]))
            self.vel_threshold = max(noise_floor * 3, 1e-6)
            self.stop_detector.set_threshold(self.vel_threshold)

    @log_exceptions
    def _update_sample_rate_from_count(self, last_count: int, now_real: float):
        """Estimate controller sampling rate from record counter increments."""
        if last_count is None:
            return
        try:
            last_count = int(last_count)
        except Exception:
            return
        if last_count <= 0:
            return
        if self._last_count is None or self._last_count_ts is None:
            self._last_count = last_count
            self._last_count_ts = now_real
            return
        dt = float(now_real - self._last_count_ts)
        if dt <= 1e-4:
            return
        wrap = 65535
        prev = int(self._last_count)
        if prev <= 0:
            prev = last_count
        delta_count = (last_count - prev) % wrap
        if delta_count <= 0:
            self._last_count = last_count
            self._last_count_ts = now_real
            return
        sr = delta_count / dt
        if 10.0 <= sr <= 20000.0:
            a = float(self._sr_alpha)
            self._current_sample_rate = (1.0 - a) * self._current_sample_rate + a * sr
        self._last_count = last_count
        self._last_count_ts = now_real

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

        now_real = time.perf_counter()
        last_count = data.get("count")
        if isinstance(last_count, (list, tuple, np.ndarray)) and len(last_count) > 0:
            last_count = last_count[-1]
        self._update_sample_rate_from_count(last_count, now_real)
        sr = float(self._current_sample_rate) if self._current_sample_rate > 1e-9 else float(self.sample_rate)
        
        dt = 1.0 / sr
        if self.stream_time is None:
            self.stream_time = now_real
        for i, (pos, force) in enumerate(zip(pos_arr, force_arr)):
            now = self.stream_time
            self.stream_time += dt
            self._process_sample(pos, force, now)
            if self.phase_state in (PhaseState.DONE, PhaseState.ERROR):
                break
        return self.phase_state
    
    @log_exceptions
    def _process_sample(self, pos, force, now):
        if self.prev_pos is None:
            self.prev_pos = pos
            if self._start_pos is None:
                try:
                    self._start_pos = float(pos)
                except Exception:
                    self._start_pos = None
            if self.half_min_pos == float("inf"):
                self._reset_half_extrema(pos)
            return
        
        self._pos_window.append(float(pos))
        sr = float(self._current_sample_rate)
        if len(self._pos_window) >= 2:
            n = min(self.vel_window_points, len(self._pos_window) - 1)
            pos_old = self._pos_window[-(n + 1)]
            v = (float(pos) - float(pos_old)) * sr / float(n)
        else:
            v = (pos - self.prev_pos) * sr
        
        # v = (pos - self.prev_pos) * float(self._current_sample_rate)
        self._update_threshold(v)
        self.stop_detector.update(v, now)
        if self.phase_state == PhaseState.RUN and self.stop_detector.is_stopped():
            step = self._current_program_step()
            if step is not None:
                mode, target_cycles = step
                if mode == Mode.WAIT_STOP:
                    self._advance_program_if_needed(mode, target_cycles)
                    return

        if self.phase_state == PhaseState.RUN:
            step = self._current_program_step()
            if step is not None:
                mode, target_cycles = step
                if mode == Mode.NMT_FINAL:
                    target = self.nmt_target_pos if self.nmt_target_pos is not None else self.nmt_estimate
                    if target is not None:
                        tol = float(self.nmt_tolerance)
                        if abs(float(pos) - float(target)) <= tol:
                            self._nmt_in_tol_points += 1
                        else:
                            self._nmt_in_tol_points = 0
                        if self._nmt_in_tol_points >= int(self.nmt_confirm_points):
                            self.last_step_result = [float(target), float(pos)]
                            self._advance_program_if_needed(mode, target_cycles)
                            return
                if mode == Mode.MID_FINAL:
                    if self._mid_armed and self.mid_target_pos is not None:
                        if float(v) < 0.0:
                            tol = float(self.mid_tolerance)
                            if abs(float(pos) - float(self.mid_target_pos)) <= tol:
                                self._mid_in_tol_points += 1
                            else:
                                self._mid_in_tol_points = 0
                            if self._mid_in_tol_points >= int(self.mid_confirm_points):
                                self.last_step_result = [float(self.mid_target_pos), float(pos)]
                                self._advance_program_if_needed(mode, target_cycles)
                                return

        sign = self._sign(v)
        if self.half_min_pos == float("inf"):
            self._reset_half_extrema(pos)
        else:
            self.half_min_pos = min(self.half_min_pos, float(pos))
            self.half_max_pos = max(self.half_max_pos, float(pos))
        self.points_after_turn += 1
        turn_detected = self._detect_turn(sign)
        if turn_detected:
            prev_sign = int(self.prev_sign)
            self._process_half_turn(prev_sign, int(sign), pos)
            self._process_turn(now)
            self._reset_half_extrema(pos)
        self._append_data_if_needed(pos, force)
        if sign != 0:
            self.prev_sign = sign
        self.prev_pos = pos
        
    @log_exceptions
    def _detect_turn(self, sign):
        min_halfcycle_points = max(1, int(float(self._current_sample_rate) * self.min_halfcycle_fraction))
        if sign != 0 and self.prev_sign != 0 and sign != self.prev_sign:
            if self.points_after_turn > min_halfcycle_points:
                self.points_after_turn = 0
                self.turn_count += 1
                return True
        return False
    
    @log_exceptions
    def _process_half_turn(self, prev_sign: int, sign: int, pos):
        """
        Обработка разворота на каждом полупериоде (смена знака скорости).
        prev_sign - знак движения ДО разворота, sign - ПОСЛЕ.
        """
        if prev_sign == 1 and sign == -1:
            vmt = float(self.half_max_pos if self.half_max_pos != float("-inf") else pos)
            self._update_vmt_from_value(vmt)
            if self.phase_state == PhaseState.RUN:
                step = self._current_program_step()
                if step is not None:
                    mode, _ = step
                    if mode == Mode.MID_FINAL and not self._mid_armed:
                        nmt_ref = None
                        if self.half_min_pos != float("inf"):
                            nmt_ref = float(self.half_min_pos)
                        elif self.nmt_estimate is not None:
                            nmt_ref = float(self.nmt_estimate)
                        elif self._start_pos is not None:
                            nmt_ref = float(self._start_pos)

                        if nmt_ref is not None:
                            self._mid_nmt_ref = float(nmt_ref)
                            self._mid_vmt_ref = float(vmt)
                            self.mid_target_pos = 0.5 * (float(vmt) + float(nmt_ref))
                            self._mid_armed = True
                            self._mid_in_tol_points = 0
    
    @log_exceptions
    def _process_turn(self, now):
        if self.turn_count % 2 != 0:
            return  # только полный цикл
        now_cycle = now
        if self.last_cycle_time is not None:
            self.cycle_times.append(now_cycle - self.last_cycle_time)
        self.last_cycle_time = now_cycle

        self._update_nmt_from_cycle_extrema()

        if self.phase_state == PhaseState.ACCEL:
            self._handle_accel_phase()
        elif self.phase_state == PhaseState.RUN:
            self._handle_run_phase()

        self._reset_cycle_buffers()
    
    @log_exceptions
    def _handle_accel_phase(self):
        if self._is_period_stable():
            self.phase_state = PhaseState.RUN
    
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
            self._advance_program_if_needed(mode, target_cycles)
    
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
        if mode == Mode.NMT_CAPTURE:
            return self._handle_nmt_capture()
        if mode == Mode.NMT_FINAL:
            return self._handle_nmt_final()
        if mode == Mode.MID_FINAL:
            return self._handle_mid_final()
        return False

    @log_exceptions
    def _append_data_if_needed(self, pos, force):
        if self.phase_state not in (PhaseState.ACCEL, PhaseState.RUN):
            return

        self.cycle_min_pos = min(self.cycle_min_pos, pos)
        self.cycle_max_pos = max(self.cycle_max_pos, pos)

        if self.nmt_estimate is None and self.cycle_min_pos != float("inf"):
            try:
                self.nmt_estimate = float(self.cycle_min_pos)
            except Exception:
                pass

        if self.phase_state != PhaseState.RUN:
            return
        step = self._current_program_step()
        if step is None:
            return
        mode, _ = step
        if mode == Mode.COLLECT:
            self.current_pos.append(pos)
            self.current_force.append(force)
    
    @log_exceptions
    def _reset_cycle_buffers(self):
        self.current_pos.clear()
        self.current_force.clear()
        self.cycle_min_pos = float("inf")
        self.cycle_max_pos = float("-inf")
    
    def _handle_detect_only(self) -> bool:
        """
        Завершает один шаг на каждый полный оборот.
        Никакие данные не сохраняются.
        Оценка НМТ обновляется централизованно на каждом полном цикле.
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
        return True
    
    @log_exceptions
    def _handle_stroke(self) -> bool:
        if self.cycle_min_pos == float("inf"):
            return False

        min_pos = float(self.cycle_min_pos)
        max_pos = float(self.cycle_max_pos)
        stroke = float(max_pos - min_pos)
        result = (
            round(min_pos, 1),
            round(max_pos, 1),
            round(stroke, 1),
        )
        self.cycles.append(result)
        self.last_step_result = self.cycles.copy()
        return True
    
    @log_exceptions
    def _handle_wait_stop(self) -> bool:
        """Завершает шаг, когда движение устойчиво остановилось"""
        # StopDetector уже обновляется в _process_sample
        if not self.stop_detector.is_stopped():
            return False
        return True

    @log_exceptions
    def _handle_nmt_capture(self) -> bool:
        """Захватывает НМТ (минимум перемещения) на каждом полном цикле."""
        if self.cycle_min_pos == float("inf"):
            return False
        self.last_step_result = [self.nmt_estimate]
        return True

    @log_exceptions
    def _handle_nmt_final(self) -> bool:
        """Доворот до НМТ: завершение происходит в _process_sample (для быстрого стопа)."""
        return False
    
    @log_exceptions
    def _handle_mid_final(self) -> bool:
        """Остановка в середине хода (ВМТ->НМТ): завершение происходит в _process_sample."""
        return False

    @log_exceptions
    def _advance_program_if_needed(self, mode, target_cycles):
        if target_cycles is None:
            if mode == Mode.COLLECT:
                return
            self.last_completed_step = self.program[self.program_index]
            self.program_index += 1
            self.program_cycle_counter = 0
            if self.program_index >= len(self.program):
                self.phase_state = PhaseState.DONE
                self.active = False
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

    def reset(self, *, clear_nmt: bool = False):
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
        self.stream_time = None
        self._current_sample_rate = float(self.sample_rate)
        self._last_count = None
        self._last_count_ts = None
        self.last_completed_step = None
        self.last_step_result = None
        self.cycle_completed = False
        self.cycle_callback = None
        self._nmt_in_tol_points = 0
        self.mid_target_pos = None
        self._mid_in_tol_points = 0
        self._mid_armed = False
        self._mid_nmt_ref = None
        self._mid_vmt_ref = None
        self.half_min_pos = float("inf")
        self.half_max_pos = float("-inf")
        self._start_pos = None
        self._pos_window.clear()
        if clear_nmt:
            self.clear_nmt()
