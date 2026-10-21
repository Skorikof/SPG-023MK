# -*- coding: utf-8 -*-
"""
Проверка определения разворотов CycleCollector на записях буфера.

Каждая сессия с вращением прогоняется через коллектор как бесконечный сбор (каждый
оборот - отдельный цикл) со старым определением разворотов (по знаку скорости) и с
новым (по положению с гистерезисом). Эталон - обороты, посчитанные отдельно по
положению с большим гистерезисом REF_HYST_MM. Для каждого собранного оборота -
отношение его длины к периоду эталонного оборота в то же время (на разгоне обороты
длиннее): 1.0 - настоящий оборот, 2.0 - двойная петля.

Запуск из корня проекта:
    uv run tools/buffer_dump/check_turns.py logs/buffer/2026-10-19 [--hyst 1.0] [-v]
"""
import argparse
import logging
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze import parse                                                    # noqa: E402
from scripts.controller.cycle_collector import CycleCollector, Mode          # noqa: E402

logging.disable(logging.CRITICAL)

REF_HYST_MM = 5.0
STAGES = ('TEST_MOVE_CYCLE', 'PUMPING', 'TEST_SPEED_ONE', 'TEST_SPEED_TWO', 'TEST_LAB_HAND_SPEED',
          'TEST_LAB_CASCADE', 'TEST_TEMPER', 'SEARCH_HOD')
LONG = 1.3          # оборот длиннее эталона в столько раз - «двойная петля»
SHORT = 0.7         # короче - ложный разворот (полоборота и меньше)


def ref_nmt(records):
    """Эталонные НМТ (номера записей) по положению с большим гистерезисом"""
    out = []
    d, ext, ext_no = 0, None, None
    lo = hi = records[0].move
    for r in records:
        p = r.move
        if d == 0:
            lo, hi = min(lo, p), max(hi, p)
            if p - lo >= REF_HYST_MM:
                d, ext, ext_no = 1, p, r.no
            elif hi - p >= REF_HYST_MM:
                d, ext, ext_no = -1, p, r.no
            continue
        if d == 1:
            if p > ext:
                ext, ext_no = p, r.no
            elif ext - p >= REF_HYST_MM:
                d, ext, ext_no = -1, p, r.no
        else:
            if p < ext:
                ext, ext_no = p, r.no
            elif p - ext >= REF_HYST_MM:
                out.append(ext_no)
                d, ext, ext_no = 1, p, r.no
    return out


def run_collector(records, hyst):
    c = CycleCollector()
    c.turn_hyst = hyst
    c.min_halfcycle_fraction = 0.0002       # как после _tune_cycle_collector_for_speed
    cycles = []             # (длина оборота в записях, номер записи в конце оборота)
    cur = [0]
    c.load_program([(Mode.COLLECT, None)], skip_accel=True)
    c.set_cycle_callback(lambda res: cycles.append((len(res[0]), cur[0])))
    for k in range(0, len(records), 20):
        b = records[k:k + 20]
        cur[0] = b[-1].no
        c.add_stream_dict({'move': [r.move for r in b], 'force': [r.force for r in b],
                           'count': [r.no for r in b]})
    return c.turn_count, cycles


def ratio(cycle, nmt):
    """Длина собранного оборота / период эталонного оборота, закончившегося ближе всего к нему
    (на разгоне обороты длиннее установившихся - сравнивать с медианой нельзя)"""
    n, end = cycle
    pairs = list(zip(nmt, nmt[1:]))
    a, b = min(pairs, key=lambda ab: abs(ab[1] - end))
    return n / (b - a)


def stage_of(df, s):
    return next((n for t, o, n in df.stages if t >= s.start_t - 1 and o == 'WAIT_BUFFER'), '?')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--hyst', type=float, default=1.0, help='гистерезис нового определения, мм')
    ap.add_argument('-v', '--verbose', action='store_true')
    args = ap.parse_args()
    files = []
    for p in map(Path, args.paths):
        files += sorted(p.rglob('*.csv')) if p.is_dir() else [p]

    tot = {'old_short': 0, 'new_short': 0, 'sess': 0, 'ref': 0, 'old_cyc': 0, 'old_long': 0, 'new_cyc': 0, 'new_long': 0,
           'old_turns': 0, 'new_turns': 0}
    bad_sessions = []
    for f in files:
        df = parse(f)
        for s in df.sessions:
            st = stage_of(df, s)
            if st not in STAGES or len(s.records) < 1000:
                continue
            nmt = ref_nmt(s.records)
            if len(nmt) < 3:
                continue
            period = statistics.median(b - a for a, b in zip(nmt, nmt[1:]))
            ref_turns = 2 * (len(nmt) - 1)
            ot, oc = run_collector(s.records, 0.0)
            nt, nc = run_collector(s.records, args.hyst)
            orat = [ratio(x, nmt) for x in oc]
            nrat = [ratio(x, nmt) for x in nc]
            o_long = [x for x in orat if x > LONG]
            n_long = [x for x in nrat if x > LONG]
            o_short = [x for x in orat if x < SHORT]
            n_short = [x for x in nrat if x < SHORT]
            tot['old_short'] += len(o_short)
            tot['new_short'] += len(n_short)
            tot['sess'] += 1
            tot['ref'] += len(nmt) - 1
            tot['old_cyc'] += len(oc)
            tot['new_cyc'] += len(nc)
            tot['old_long'] += len(o_long)
            tot['new_long'] += len(n_long)
            tot['old_turns'] += ot
            tot['new_turns'] += nt
            if n_short:
                print(f'  короткие (новое): {f.name} {st} период {period:.0f}: {[round(x, 2) for x in n_short]}, '
                      f'длины {[x[0] for x, r in zip(nc, nrat) if r < SHORT]}')
            if o_long or n_long or args.verbose:
                bad_sessions.append((f.name, st, round(period), len(nmt) - 1, len(oc), len(o_long),
                                     len(nc), len(n_long), [round(x, 1) for x in (o_long + n_long)][:6]))
    print(f'{"файл":24s} {"этап":20s} {"период":>6s} {"оборотов":>8s} '
          f'{"стар: циклов/длинных":>21s} {"нов: циклов/длинных":>20s}  длинные (x периода)')
    for b in bad_sessions:
        print(f'{b[0]:24s} {b[1]:20s} {b[2]:6d} {b[3]:8d} {b[4]:14d}/{b[5]:<6d} {b[6]:13d}/{b[7]:<6d}  {b[8]}')
    print(f'\nсессий {tot["sess"]}, эталонных оборотов {tot["ref"]}')
    print(f'  старое: циклов {tot["old_cyc"]}, длиннее {LONG} оборота: {tot["old_long"]}, '
          f'короче {SHORT}: {tot["old_short"]}')
    print(f'  новое (гистерезис {args.hyst} мм): циклов {tot["new_cyc"]}, длиннее {LONG} оборота: '
          f'{tot["new_long"]}, короче {SHORT}: {tot["new_short"]}')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
