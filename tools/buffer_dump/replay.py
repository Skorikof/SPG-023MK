# -*- coding: utf-8 -*-
"""
Прогон записи буфера (BUFFER_DUMP) через настоящий CycleCollector без стенда.

Программы коллектора загружаются по событиям next_stage так же, как это делает Model
(transition_via_buffer), записи подаются пачками в порядке чтения. Сравнивается
результат коллектора с тем, что было на стенде (collector_done в файле).

Режимы:
  old - как до 16.10: пачка, прочитанная за LEAK_MS до reader_stop, ещё стоит в очереди
        сигналов Qt и попадает в программу следующего этапа;
  new - результаты прошлой сессии отбрасываются, в начале сессии on_stream_restart.

Запуск из корня проекта:
    uv run tools/buffer_dump/replay.py logs/buffer/2026-10-16 [--mode old|new|both] [-v]
"""
import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze import force_raw, move_mm                               # noqa: E402
from scripts.controller.cycle_collector import CycleCollector, Mode, PhaseState   # noqa: E402

logging.disable(logging.CRITICAL)

LEAK_MS = 10.0      # пачка, прочитанная за столько мс до reader_stop, ещё в очереди Qt
SPEED_STAGES = ('TEST_SPEED_ONE', 'TEST_SPEED_TWO', 'TEST_LAB_HAND_SPEED', 'TEST_LAB_CASCADE')


def load_for_stage(c: CycleCollector, stage: str):
    """Программа коллектора для этапа - как в Model (test_move_cycle, pumping, ...)"""
    if stage == 'TEST_MOVE_CYCLE':
        c.clear_nmt()
        c.load_program([(Mode.DETECT_ONLY, 2)], skip_accel=True)
    elif stage == 'PUMPING':
        c.load_program([(Mode.DETECT_ONLY, 2)], skip_accel=True)
    elif stage in SPEED_STAGES:
        c.load_program([(Mode.DETECT_ONLY, 2), (Mode.COLLECT, 2)], skip_accel=True)
        # _tune_cycle_collector_for_speed: на деле порог разворота 1 запись (README, п. 9)
        c.min_halfcycle_fraction = 0.0002
    elif stage == 'TEST_TEMPER':
        c.load_program([(Mode.COLLECT, None)], skip_accel=False)
    elif stage == 'STOP_GEAR_END_TEST':
        c.load_program([(Mode.WAIT_STOP, None)], skip_accel=True)
    elif stage == 'STOP_GEAR_MIN_POS':
        c.set_nmt_params(tolerance=1.0, confirm_points=2)
        c.load_program([(Mode.NMT_FINAL, None)], skip_accel=True, preserve_nmt=True)
    elif stage == 'SEARCH_HOD':
        c.clear_nmt()
        c.load_program([(Mode.STROKE_ONLY, 2)], skip_accel=True)
    elif stage == 'POS_SET_GEAR':
        c.set_mid_params(tolerance=2.0, confirm_points=2, lead=13)
        c.load_program([(Mode.MID_FINAL, None)], skip_accel=True, preserve_nmt=True)
    else:
        return False
    return True


def read_batches(path: Path):
    """События и пачки записей (по строкам RD) в порядке файла"""
    items = []
    pending = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            p = line.rstrip('\n').split(';')
            kind, t = p[0], float(p[1])
            if kind == 'EV':
                items.append(('ev', t, p[2], p[3:]))
            elif kind == 'REC' or (kind == 'RAW' and p[9] == 'A' and p[3] != '0'):
                pending.append((int(p[3]), move_mm(int(p[6])), force_raw(int(p[4]), int(p[5]))))
            elif kind == 'RD':
                if pending:
                    items.append(('data', t, pending, None))
                pending = []
    return items


def replay(path: Path, mode: str, verbose: bool):
    c = CycleCollector()
    items = read_batches(path)
    results = []            # (стадия, шаг, результат)
    nmt_targets = []        # цель доводки до НМТ в момент её начала
    stops = [i[1] for i in items if i[0] == 'ev' and i[2] == 'reader_stop']
    actual = [(i[2], i[3]) for i in items if i[0] == 'ev' and i[2] == 'collector_done']
    stage = None
    reading = False
    done = False            # шаг программы завершён (Model перестал бы ждать)
    late = []               # пачки после завершения шага до reader_stop (режим old)

    def feed(batch):
        nonlocal done
        if not c.active or done:
            return
        data = {'count': [r[0] for r in batch], 'move': [r[1] for r in batch], 'force': [r[2] for r in batch]}
        st = c.add_stream_dict(data)
        if st == PhaseState.DONE:
            step = c.get_last_completed_step()
            res = c.get_last_step_result()
            results.append((stage, step[0].name if step else None, res, round(c.nmt_estimate, 1)
                            if c.nmt_estimate is not None else None))
            done = True

    for kind, t, a, b in items:
        if kind == 'ev':
            if a == 'next_stage':
                stage = b[0]
                if stage == 'STOP_GEAR_MIN_POS':
                    tgt = c.nmt_target_pos if c.nmt_target_pos is not None else c.nmt_estimate
                    nmt_targets.append(None if tgt is None else round(tgt, 1))
                if load_for_stage(c, stage):
                    done = False
                if mode == 'old':
                    for batch in late:
                        feed(batch)
                late = []
            elif a == 'reader_start':
                reading = True
                if mode == 'new':
                    c.on_stream_restart()
            elif a == 'reader_stop':
                reading = False
            elif a == 'collector_done':
                pass
        elif kind == 'data':
            if not reading:
                continue
            if mode == 'old' and any(s - LEAK_MS <= t <= s for s in stops):
                late.append(a)          # ещё в очереди Qt - попадёт в программу следующего этапа
                continue
            feed(a)

    nmt_actual = [b for n, b in actual if b and b[0] == 'NMT_FINAL']
    nmt_replay = [r for r in results if r[1] == 'NMT_FINAL']
    if verbose:
        for r in results:
            print(f'      {r[0]:20s} {r[1]:12s} {str(r[2])[:60]:60s} НМТ={r[3]}')
    return (nmt_targets[-1] if nmt_targets else None,
            nmt_actual[-1][2] if nmt_actual else None)


def main():
    ap = argparse.ArgumentParser(description='Прогон записи буфера через CycleCollector')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--mode', choices=('old', 'new', 'both'), default='both')
    ap.add_argument('-v', '--verbose', action='store_true')
    args = ap.parse_args()
    files = []
    for p in map(Path, args.paths):
        files += sorted(p.rglob('*.csv')) if p.is_dir() else [p]
    modes = ('old', 'new') if args.mode == 'both' else (args.mode,)
    print(f'{"файл":32s} {"на стенде":>12s} ' + ' '.join(f'{m:>10s}' for m in modes))
    for f in files:
        row = []
        stand = None
        for m in modes:
            if args.verbose:
                print(f'  {f.name} [{m}]')
            got, stand_res = replay(f, m, args.verbose)
            stand = stand_res if stand_res is not None else stand
            row.append(got)
        if stand is None and all(r is None for r in row):
            continue
        stand_t = stand.split(',')[0].strip('[ ') if stand else '-'
        try:
            stand_t = f'{float(stand_t):.1f}'
        except ValueError:
            pass
        print(f'{f.name:32s} {stand_t:>12s} ' + ' '.join(f'{str(r):>10s}' for r in row))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
