# -*- coding: utf-8 -*-
"""
Разбор файлов записи буфера (BUFFER_DUMP = 1, logs/buffer/ГГГГ-ММ-ДД/*.csv).

Запуск из корня проекта:
    uv run tools/buffer_dump/analyze.py logs/buffer/2026-10-16            # все файлы дня
    uv run tools/buffer_dump/analyze.py logs/buffer/2026-10-16/09-43-04_lab_hand.csv -v
    uv run tools/buffer_dump/analyze.py ФАЙЛ --csv out_dir                 # записи по сессиям в CSV

Что считает для каждой сессии чтения буфера (от reader_start до reader_stop):
  - задержки: команда buffer_on -> подтверждение записи -> бит 0 = 1 по регистрам ->
    начало чтения -> первое чтение (номер первой записи);
  - «записи раньше времени»: запись №N не может появиться раньше, чем через N мс
    после старта сессии в контроллере. Для каждой записи d = t_чтения - N (мс) - это
    оценка момента старта; у свежих записей d почти постоянно, у старых (от прошлой
    сессии) d намного меньше. Записи с d < опорного - D_TOLERANCE считаются старыми;
  - скачки положения > JUMP_MM между соседними принятыми записями (стык данных);
  - ожидания (пустые чтения), отставание чтения от записи, разрывы нумерации;
  - скорость часов контроллера относительно ПК (записей на мс ПК).
Итог по файлу: этапы с длительностями, события коллектора, аварии, страховка буфера.

Формат строк файла - в scripts/buffer_dump.py.
"""
import argparse
import statistics
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

JUMP_MM = 5.0           # скачок положения между соседними записями (1 мс), мм
D_TOLERANCE = 20.0      # запись «раньше времени», если d меньше опорного на столько мс
REF_FROM_MS = 500.0     # опорное d - по записям, прочитанным с этого момента сессии...
REF_TO_MS = 1500.0      # ...до этого (чтение уже догнало запись)


def move_mm(reg: int) -> float:
    """Перемещение штока, мм (как ParserSPG023MK._movement_amount 'pos')"""
    if reg & 0x8000:
        reg -= 0x10000
    return round(-0.1 * reg, 1)


def force_raw(big: int, low: int) -> float:
    """Усилие с датчика (float из двух регистров), без коэффициента и нуля"""
    return struct.unpack('>f', struct.pack('>HH', big, low))[0]


@dataclass
class Record:
    t: float
    slot: int
    no: int
    move: float
    force: float
    state: int
    raw_mark: str = ''      # для RAW: A/R/-


@dataclass
class Session:
    start_t: float
    stage: str
    t_cmd_on: float | None = None
    t_ack_on: float | None = None
    t_bit0_on: float | None = None
    t_first_read: float | None = None
    first_no: int | None = None
    stop_t: float | None = None
    records: list = field(default_factory=list)     # принятые (REC и RAW с меткой A)
    raw: list = field(default_factory=list)         # все RAW
    reads: list = field(default_factory=list)       # (t, slot, taken, rej_no, rej_move, idle)
    errors: list = field(default_factory=list)
    events: list = field(default_factory=list)


@dataclass
class DumpFile:
    path: Path
    header: str = ''
    sessions: list = field(default_factory=list)
    stages: list = field(default_factory=list)      # (t, old, new)
    events: list = field(default_factory=list)      # (t, name, fields)


def parse(path: Path) -> DumpFile:
    df = DumpFile(path)
    stage = 'WAIT'
    pending = {}            # события буфера до начала сессии чтения
    cur: Session | None = None
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            if line.startswith('#'):
                df.header = df.header or line[1:].strip()
                continue
            p = line.split(';')
            kind, t = p[0], float(p[1])
            if kind == 'EV':
                name, flds = p[2], p[3:]
                df.events.append((t, name, flds))
                if name == 'stage':
                    stage = flds[1]
                    df.stages.append((t, flds[0], flds[1]))
                elif name == 'cmd' and flds[0] == 'buffer_on':
                    pending = {'t_cmd_on': t}
                elif name == 'ack' and flds[0] == 'buffer_on' and flds[1] == 'OK!':
                    pending['t_ack_on'] = t
                elif name == 'state_bit0' and flds[0] == '0->1':
                    pending['t_bit0_on'] = t
                elif name == 'reader_start':
                    cur = Session(start_t=t, stage=stage, **pending)
                    df.sessions.append(cur)
                    pending = {}
                elif name == 'reader_first_read' and cur is not None:
                    cur.t_first_read = t
                    cur.first_no = int(flds[1].split('=')[1])
                elif name == 'reader_stop' and cur is not None:
                    cur.stop_t = t
                    cur = None
                elif cur is not None:
                    cur.events.append((t, name, flds))
            elif cur is None:
                continue
            elif kind == 'REC':
                cur.records.append(Record(t, int(p[2]), int(p[3]), move_mm(int(p[6])),
                                          force_raw(int(p[4]), int(p[5])), int(p[7])))
            elif kind == 'RAW':
                r = Record(t, int(p[2]), int(p[3]), move_mm(int(p[6])),
                           force_raw(int(p[4]), int(p[5])), int(p[7]), p[9])
                cur.raw.append(r)
                if r.raw_mark == 'A' and r.no != 0:
                    cur.records.append(r)
            elif kind == 'RD':
                cur.reads.append((t, int(p[2]), int(p[4]), p[7], p[8], int(p[9] or 0)))
            elif kind == 'RDERR':
                cur.errors.append((t, int(p[2]), ';'.join(p[3:])))
    return df


def session_start_ref(s: Session) -> float:
    """Опорный момент старта сессии в контроллере по свежим записям (мс файла):
    медиана d = t - N по записям, прочитанным в окне REF_FROM_MS..REF_TO_MS сессии"""
    win = [r.t - r.no for r in s.records if REF_FROM_MS <= r.t - s.start_t <= REF_TO_MS]
    if len(win) < 20:
        win = [r.t - r.no for r in s.records[len(s.records) // 2:]]
    return statistics.median(win) if win else float('nan')


def clock_rate(s: Session) -> float | None:
    """Записей контроллера на 1 мс ПК (наклон N(t)) по второй половине сессии"""
    rec = s.records[len(s.records) // 2:]
    if len(rec) < 200 or rec[-1].t - rec[0].t < 500:
        return None
    return (rec[-1].no - rec[0].no) / (rec[-1].t - rec[0].t)


def fmt(v, nd=1):
    return '-' if v is None else f'{v:.{nd}f}'


def report_session(i: int, s: Session, verbose: bool):
    out = []
    rec = s.records
    dur = (s.stop_t or (rec[-1].t if rec else s.start_t)) - s.start_t
    out.append(f'  Сессия {i}: этап {s.stage}, начало чтения {s.start_t / 1000:.3f} с, '
               f'длительность {dur / 1000:.2f} с, принято записей {len(rec)}')

    def rel(t):
        return None if t is None or s.t_cmd_on is None else t - s.t_cmd_on
    out.append(f'    buffer_on: подтверждение +{fmt(rel(s.t_ack_on))} мс, бит 0 = 1 +{fmt(rel(s.t_bit0_on))} мс, '
               f'начало чтения +{fmt(rel(s.start_t))} мс, первое чтение +{fmt(rel(s.t_first_read))} мс '
               f'(первая запись №{s.first_no})')
    if not rec:
        out.append('    !!! данных нет')
        return out, {}

    ref = session_start_ref(s)
    early = [r for r in rec if r.t - r.no < ref - D_TOLERANCE]
    jumps = [(a, b) for a, b in zip(rec, rec[1:]) if abs(b.move - a.move) > JUMP_MM]
    gaps = [(a, b) for a, b in zip(rec, rec[1:]) if (b.no - a.no) % 65536 != 1]
    idle = sum(x[5] for x in s.reads) + sum(1 for x in s.reads if x[2] == 0)
    lag = [r.t - r.no - ref for r in rec]
    rate = clock_rate(s)
    lead = (rel(ref + 0.0) if s.t_cmd_on is not None else None)

    out.append(f'    старт сессии в контроллере (по свежим записям): +{fmt(lead)} мс от команды; '
               f'отставание чтения: медиана {fmt(statistics.median(lag))} мс, макс {fmt(max(lag))} мс; '
               f'часы контроллера: {fmt(rate, 4)} записи/мс ПК')
    if early:
        out.append(f'    !!! записей «раньше времени» (старые): {len(early)}, №{early[0].no}..{early[-1].no}, '
                   f'слоты {early[0].slot}..{early[-1].slot}, прочитаны на +{early[0].t - s.start_t:.1f}..'
                   f'+{early[-1].t - s.start_t:.1f} мс сессии, положение {early[0].move}..{early[-1].move} мм')
    for a, b in jumps:
        out.append(f'    !!! скачок положения №{a.no}->{b.no} (слоты {a.slot}->{b.slot}): {a.move} -> {b.move} мм '
                   f'на +{b.t - s.start_t:.1f} мс сессии')
    for a, b in gaps:
        out.append(f'    !!! разрыв нумерации №{a.no} -> №{b.no} на +{b.t - s.start_t:.1f} мс сессии')
    if s.errors:
        out.append(f'    !!! ошибок чтения: {len(s.errors)}, первая: {s.errors[0][2]}')
    out.append(f'    пустых чтений (ждали запись): {idle}')
    if verbose and s.raw:
        zeros = sum(1 for r in s.raw if r.no == 0)
        out.append(f'    окно подробностей: {len(s.raw)} записей прочитано, из них с №0 (обнулено) {zeros}')
        shown = 0
        for r in s.raw:
            if r.raw_mark in ('A', 'R') and shown < 60:
                out.append(f'      +{r.t - s.start_t:6.1f} мс  слот {r.slot:4d}  №{r.no:5d}  {r.raw_mark}  '
                           f'перемещ {r.move:7.1f}  d={r.t - r.no - ref:+8.1f}')
                shown += 1
    if verbose:
        for t, name, flds in s.events:
            out.append(f'      событие +{t - s.start_t:.1f} мс: {name} {";".join(flds)}')
    stats = {'early': len(early), 'jumps': len(jumps), 'gaps': len(gaps), 'errors': len(s.errors),
             'ack': rel(s.t_ack_on), 'bit0': rel(s.t_bit0_on), 'lead': lead, 'rate': rate}
    return out, stats


def report_file(df: DumpFile, verbose: bool):
    print(f'=== {df.path}')
    if df.header:
        print(f'  {df.header}')
    totals = {'early': 0, 'jumps': 0, 'gaps': 0, 'errors': 0}
    all_stats = []
    for i, s in enumerate(df.sessions, 1):
        lines, st = report_session(i, s, verbose)
        print('\n'.join(lines))
        for k in totals:
            totals[k] += st.get(k, 0)
        all_stats.append(st)

    # этапы и важные события
    print('  Этапы:')
    for (t, old, new), nxt in zip(df.stages, df.stages[1:] + [None]):
        d = f'{(nxt[0] - t) / 1000:.2f} с' if nxt else ''
        print(f'    {t / 1000:9.3f}  {new:22s} {d}')
    for t, name, flds in df.events:
        if name in ('collector_done', 'position_jump', 'alarm', 'watchdog_restart', 'watchdog_alarm'):
            print(f'    {t / 1000:9.3f}  {name}: {"; ".join(flds)}')
    print(f'  Итого: сессий {len(df.sessions)}, старых записей {totals["early"]}, скачков {totals["jumps"]}, '
          f'разрывов {totals["gaps"]}, ошибок чтения {totals["errors"]}')
    return totals, all_stats


def export_csv(df: DumpFile, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(df.sessions, 1):
        ref = session_start_ref(s) if s.records else 0
        p = out_dir / f'{df.path.stem}_s{i:02d}_{s.stage}.csv'
        with open(p, 'w', encoding='utf-8') as f:
            f.write('t_ms;slot;no;move_mm;force_raw;state;d_ms\n')
            for r in s.records:
                f.write(f'{r.t - s.start_t:.1f};{r.slot};{r.no};{r.move};{r.force:.2f};{r.state};'
                        f'{r.t - r.no - ref:.1f}\n')
        print(f'  -> {p}')


def main():
    ap = argparse.ArgumentParser(description='Разбор записи буфера SPG-023MK (BUFFER_DUMP)')
    ap.add_argument('paths', nargs='+', help='файлы .csv или папки с ними')
    ap.add_argument('-v', '--verbose', action='store_true', help='записи окна подробностей и события сессий')
    ap.add_argument('--csv', metavar='DIR', help='выгрузить принятые записи сессий в CSV')
    args = ap.parse_args()

    files = []
    for p in map(Path, args.paths):
        files += sorted(p.rglob('*.csv')) if p.is_dir() else [p]
    if not files:
        sys.exit('файлов не найдено')

    grand = {'early': 0, 'jumps': 0, 'gaps': 0, 'errors': 0}
    stats = []
    for f in files:
        df = parse(f)
        totals, st = report_file(df, args.verbose)
        for k in grand:
            grand[k] += totals[k]
        stats += st
        if args.csv:
            export_csv(df, Path(args.csv))
        print()

    if len(files) > 1:
        def med(key):
            v = [s[key] for s in stats if s.get(key) is not None]
            return fmt(statistics.median(v)) if v else '-'
        print(f'=== Всего файлов {len(files)}, сессий {len(stats)}: старых записей {grand["early"]} '
              f'(в {sum(1 for s in stats if s.get("early"))} сессиях), скачков {grand["jumps"]}, '
              f'разрывов {grand["gaps"]}, ошибок чтения {grand["errors"]}')
        print(f'    медианы от команды buffer_on: подтверждение {med("ack")} мс, бит 0 {med("bit0")} мс, '
              f'старт записи в контроллере {med("lead")} мс')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
