import numpy as np
from collections import deque


class StopDetector:
    """
    Детектор остановки двигателя (не механического успокоения).
    Ловит момент, когда активное движение исчезло,
    даже если система ещё пассивно ползёт от усилия амортизатора.
    """
    def __init__(
        self,
        vel_threshold_getter,      # функция -> noise threshold
        stop_ratio=0.05,           # % от рабочей скорости
        confirm_time_sec=0.25,     # сколько держится низкая скорость
        work_hist_size=200,
        min_samples=20,
    ):
        self.vel_threshold_getter = vel_threshold_getter

        self.stop_ratio = stop_ratio
        self.confirm_time_sec = confirm_time_sec

        self.work_vel_hist = deque(maxlen=work_hist_size)
        self.min_samples = min_samples

        self.stop_candidate_since = None
        self.stopped = False

    def reset(self):
        self.work_vel_hist.clear()
        self.stop_candidate_since = None
        self.stopped = False

    def update(self, v, phase_state, now):
        """
        v — текущая скорость (pos - prev_pos)
        phase_state — нужен чтобы знать, когда накапливать рабочую скорость
        now — текущее время
        """
        abs_v = abs(v)
        noise_threshold = self.vel_threshold_getter()

        # ---- собираем рабочую скорость только во время RUN ----
        if phase_state.name == "RUN":
            if abs_v > noise_threshold:
                self.work_vel_hist.append(abs_v)

        # ---- если мало данных — нельзя определить ----
        if len(self.work_vel_hist) < self.min_samples:
            self.stopped = False
            return False

        work_vel = np.median(self.work_vel_hist)

        stop_vel = max(
            noise_threshold * 2.5,
            work_vel * self.stop_ratio
        )

        # ---- проверка остановки ----
        if abs_v < stop_vel:
            if self.stop_candidate_since is None:
                self.stop_candidate_since = now
            else:
                if now - self.stop_candidate_since > self.confirm_time_sec:
                    self.stopped = True
        else:
            self.stop_candidate_since = None
            self.stopped = False

        return self.stopped