import time
import numpy as np


class StandController:
    def measure_stroke(
        colletor,
        detect_cycles=3,
        collect_cycles=5,
        timeout_sec=30.0,
        max_std=None,
    ):
        """
        Измеряет механический ход стенда.

        Returns dict:
        {
            stroke_mean,
            stroke_std,
            strokes,
            ok
        }
        """

        collector = collector   # предполагаем что он уже есть

        # --- 1. Убедиться что стенд двигается ---
        # (если у тебя есть команда запуска движения — вызови тут)
        # self.start_motion()

        # --- 2. Reset алгоритма ---
        collector.reset()

        # --- 3. Загрузка программы измерения ---
        program = [
            (Mode.DETECT_ONLY, detect_cycles),
            (Mode.COLLECT, collect_cycles),
        ]

        collector.load_program(program)

        # --- 4. Ждём DONE ---
        t0 = time.perf_counter()

        while True:

            if collector.phase_state == PhaseState.DONE:
                break

            if time.perf_counter() - t0 > timeout_sec:
                raise TimeoutError("Stroke measurement timeout")

            time.sleep(0.01)

        # --- 5. Считаем stroke ---
        strokes = []

        for pos, _ in collector.get_cycles():
            if len(pos) < 5:
                continue
            strokes.append(float(np.max(pos) - np.min(pos)))

        if not strokes:
            raise RuntimeError("No valid cycles collected")

        stroke_mean = float(np.mean(strokes))
        stroke_std = float(np.std(strokes))

        ok = True
        if max_std is not None:
            ok = stroke_std <= max_std

        return {
            "stroke_mean": stroke_mean,
            "stroke_std": stroke_std,
            "strokes": strokes,
            "ok": ok,
        }