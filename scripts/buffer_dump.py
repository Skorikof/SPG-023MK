# -*- coding: utf-8 -*-
"""
Запись сырого потока буфера контроллера в файл (диагностика, BUFFER_DUMP = 1 в .env).

Один файл на операцию стенда (испытание, определение/настройка хода, окно отладки):
открывается при первой команде buffer_on, закрывается, когда контроллер в WAIT,
буфер выключен и событий нет IDLE_CLOSE с (Controller._update_stage_on_timer).
Файлы: logs/buffer/ГГГГ-ММ-ДД/ЧЧ-ММ-СС_<операция>.csv. Разбор - tools/buffer_dump/.

Строки (разделитель ;, время - мс от открытия файла, общее для всех потоков):
  EV;t;событие;поля...            - события: команды, подтверждения, бит 0, этапы...
  RD;t;слот;запрошено;принято;первая;последняя;отвергнута_№;отвергнута_перемещ;пустых_чтений
                                  - сводка чтения буфера
  REC;t;слот;№;усилие_ст;усилие_мл;перемещ;состояние;темпер
                                  - принятая запись (сырые регистры)
  RAW;t;слот;№;усилие_ст;усилие_мл;перемещ;состояние;темпер;метка
                                  - все записи чтения в первые VERBOSE_WINDOW с после
                                    начала чтения буфера; метка: A - принята,
                                    R - на ней чтение остановилось, - - не проверялась
  RDERR;t;слот;текст              - ошибка чтения
Слот - номер записи в кольце буфера (0..2999), адрес = 0x4000 + 6 * слот.

Запись в файл - в своём фоновом потоке через очередь: читающий поток только
кладёт готовую строку, на время обмена с контроллером это не влияет.
"""
import queue
import threading
import time
from datetime import datetime
from pathlib import Path

from config import config
from scripts import archive_names
from scripts.logger import my_logger
from scripts.modbus.registers import REG_BUFFER_START, REG_BUFFER_RECORD_REGS


DUMP_DIR = Path('logs') / 'buffer'


def slot(addr: int) -> int:
    """Номер записи в кольце буфера по адресу регистра"""
    return (addr - REG_BUFFER_START) // REG_BUFFER_RECORD_REGS


class BufferDump:
    VERBOSE_WINDOW = 0.5    # с после начала чтения буфера, когда пишутся все записи чтения
    IDLE_CLOSE = 1.0        # с без событий в WAIT с выключенным буфером - файл закрывается
    STOP_TIMEOUT = 3.0      # сколько ждать дозаписи очереди при закрытии программы, с

    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.enabled = config.buffer_dump
        self.is_open = False
        self._t0 = 0.0
        self._last_line = 0.0
        self._queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None

    def open(self, name: str):
        """Начать новый файл (если запись включена и файл ещё не открыт)"""
        if not self.enabled or self.is_open:
            return
        try:
            self._open(name)
        except Exception as e:
            # диагностика не должна мешать работе стенда (open вызывается перед командой buffer_on)
            self.logger.error(f'Запись буфера в файл не начата: {e}')

    def _open(self, name: str):
        now = datetime.now()
        path = DUMP_DIR / archive_names.file_stem(now) / f'{now:%H-%M-%S}_{name}.csv'
        self._t0 = time.perf_counter()
        self._last_line = self._t0
        self._start_thread()
        self._queue.put(('open', path))
        self.is_open = True
        self._put(f'# SPG-023MK, сырой поток буфера: {now:%Y-%m-%d %H:%M:%S}, операция {name}, '
                  f'{config.comport} {config.baudrate}, timeout {config.timeout}, retries {config.retries}')
        self._put('# EV;t;событие;поля | RD;t;слот;запрошено;принято;первая;последняя;'
                  'отвергнута_№;отвергнута_перемещ;пустых_чтений | '
                  'REC/RAW;t;слот;№;усилие_ст;усилие_мл;перемещ;состояние;темпер[;метка] | RDERR;t;слот;текст')
        self.logger.info(f'Запись буфера в файл: {path}')

    def close(self, reason: str = ''):
        if not self.is_open:
            return
        self.event('close', reason)
        self.is_open = False
        self._queue.put(('close', None))

    def stop(self):
        """Закрытие программы: закрыть файл и дождаться дозаписи очереди"""
        self.close('выход из программы')
        if self._thread is not None:
            self._queue.put(('stop', None))
            self._thread.join(self.STOP_TIMEOUT)

    def now_ms(self) -> float:
        return (time.perf_counter() - self._t0) * 1000.0

    def idle_for(self) -> float:
        """Сколько секунд в файл ничего не писалось"""
        return time.perf_counter() - self._last_line

    def event(self, name: str, *fields):
        if not self.is_open:
            return
        self._put(';'.join(['EV', f'{self.now_ms():.1f}', name, *map(str, fields)]))

    def line(self, kind: str, t_ms: float, *fields):
        """Строка с заданным временем (поток чтения считает время сам, в момент ответа)"""
        if not self.is_open:
            return
        self._put(';'.join([kind, f'{t_ms:.1f}', *map(str, fields)]))

    def block(self, lines: list[str]):
        """Несколько готовых строк одним куском (записи одного чтения)"""
        if not self.is_open or not lines:
            return
        self._put('\n'.join(lines))

    def _put(self, text: str):
        self._last_line = time.perf_counter()
        self._queue.put(('line', text))

    def _start_thread(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, name='buffer_dump', daemon=True)
            self._thread.start()

    def _run(self):
        f = None
        while True:
            kind, data = self._queue.get()
            try:
                if kind == 'open':
                    if f is not None:
                        f.close()
                    data.parent.mkdir(parents=True, exist_ok=True)
                    f = open(data, 'w', encoding='utf-8', buffering=1 << 16)
                elif kind == 'line':
                    if f is not None:
                        f.write(data)
                        f.write('\n')
                elif kind == 'close':
                    if f is not None:
                        f.close()
                        f = None
                elif kind == 'stop':
                    if f is not None:
                        f.close()
                    return
                # очередь разобрана - на диск, чтобы при вылете программы файл был полным
                if f is not None and self._queue.empty():
                    f.flush()
            except Exception as e:
                self.logger.error(f'Запись буфера в файл: {e}')


dump = BufferDump()
