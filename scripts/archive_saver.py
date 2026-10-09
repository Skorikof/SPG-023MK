# -*- coding: utf-8 -*-
import queue
import threading
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from scripts.logger import my_logger


ARCHIVE_DIR = Path('archive')
END_TEST_MARKER = 'end_test'
BOM = b'\xef\xbb\xbf'

HEADER = ('Время;'
          'ФИО оператора;'
          'Должность;'
          'Тип испытания;'
          'Название гасителя;'
          'Серийный номер;'
          'Длина в сжатом состоянии, мм;'
          'Длина в разжатом состоянии, мм;'
          'Ход испытания, мм;'
          '1-я скорость исытания, м/с;'
          'Мин усилие отбоя, кгс;'
          'Макс усилие отбоя, кгс;'
          'Мин усилие сжатия, кгс;'
          'Макс усилие сжатия, кгс;'
          '2-я скорость испытания, м/с;'
          'Мин усилие отбоя, кгс;'
          'Макс усилие отбоя, кгс;'
          'Мин усилие сжатия, кгс;'
          'Макс усилие сжатия, кгс;'
          'Флаг выталкивающей силы;'
          'Выталкивающая сила статичная, кгс;'
          'Выталкивающая сила динамическая, кгс;'
          'Макс температура, °С;'
          'Скорость испытания, м/с;'
          'Перемещение, мм(Температура, ℃)/Усилие, кгс')


class WriterArchSignals(QObject):
    # Сообщение для статусбара (файл архива занят другой программой и т.п.)
    status_msg = Signal(str)


class WriterArch:
    """
    Запись архива испытаний в archive/ДД.ММ.ГГГГ.csv.

    Все записи идут через очередь в одном фоновом потоке - порядок строк сохраняется.
    Если файл занят (открыт в Excel), запись повторяется, пока файл не освободится,
    остальные записи ждут в очереди. При остановке очередь дописывается до конца.
    Файлы пишутся в UTF-8 с BOM, чтобы Excel правильно показывал кириллицу.
    """
    RETRY_PAUSE = 1.0       # пауза между попытками записи в занятый файл, с
    STOP_TIMEOUT = 10.0     # сколько ждать дозаписи очереди при закрытии программы, с

    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.signals = WriterArchSignals()
        self._queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None
        self._stopping = False
        self._stop_deadline = 0.0

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name='archive_writer', daemon=True)
        self._thread.start()

    def stop(self):
        """Дописывает очередь (не дольше STOP_TIMEOUT) и останавливает поток"""
        if self._thread is None:
            return
        self._stop_deadline = time.monotonic() + self.STOP_TIMEOUT
        self._stopping = True
        self._queue.put(None)
        self._thread.join(self.STOP_TIMEOUT + 1)
        if self._thread.is_alive():
            self.logger.error(f'Архив: не дописано записей при закрытии - {self._queue.qsize()}')
        self._thread = None

    def write_arch_out(self, tag, data=None):
        """
        tag: 'data' - запись испытания, 'end_test' - конец испытания,
             'begin_test' - начало нового испытания (закрывает незакрытое предыдущее)
        Имя файла фиксируется в момент постановки в очередь
        """
        self._queue.put((tag, data, self._file_for(datetime.now())))

    # ---------------------------------------------------------------------------------

    @staticmethod
    def _file_for(dt: datetime) -> Path:
        return ARCHIVE_DIR / f'{dt.day:02}.{dt.month:02}.{dt.year}.csv'

    def _run(self):
        self._convert_old_files()
        while True:
            item = self._queue.get()
            if item is None:
                break
            tag, data, path = item
            text = self._build_text(tag, data, path)
            if text:
                self._append_with_retry(path, text)

    def _build_text(self, tag, data, path: Path) -> str:
        try:
            if tag == 'data':
                return self._format_test(data)
            if tag == 'end_test':
                return f'{END_TEST_MARKER};\n'
            if tag == 'begin_test':
                if self._last_line_is_open_test(path):
                    self.logger.warning(f'Архив: предыдущее испытание в {path.name} не было закрыто, '
                                        f'дописан {END_TEST_MARKER}')
                    return f'{END_TEST_MARKER};\n'
                return ''
            self.logger.error(f'Архив: неизвестный тег записи {tag}')
        except Exception as e:
            self.logger.error(f'Архив: ошибка подготовки записи {tag} - {e}')
        return ''

    def _append_with_retry(self, path: Path, text: str):
        blocked = False
        while True:
            try:
                ARCHIVE_DIR.mkdir(exist_ok=True)
                is_new = not path.exists()
                # utf-8-sig пишет BOM только в начало пустого файла
                with open(path, 'a', encoding='utf-8-sig') as f:
                    if is_new:
                        f.write(HEADER + '\n')
                    f.write(text)
                if blocked:
                    self.logger.info(f'Архив: {path.name} освободился, запись выполнена')
                    self.signals.status_msg.emit('Архив испытаний записан')
                return

            except PermissionError:
                if not blocked:
                    blocked = True
                    msg = f'Файл архива {path.name} открыт в другой программе - закройте его, запись ожидает'
                    self.logger.warning(msg)
                    self.signals.status_msg.emit(msg)
                if self._stopping and time.monotonic() > self._stop_deadline:
                    self.logger.error(f'Архив: {path.name} занят при закрытии программы, запись потеряна')
                    return
                time.sleep(self.RETRY_PAUSE)

            except Exception as e:
                self.logger.error(f'Архив: ошибка записи в {path.name} - {e}')
                return

    @staticmethod
    def _last_line_is_open_test(path: Path) -> bool:
        """True, если файл заканчивается записью испытания без end_test"""
        if not path.exists():
            return False
        with open(path, 'rb') as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 64 * 1024))
            tail = f.read().decode('utf-8', errors='ignore')
        lines = [ln for ln in tail.splitlines() if ln.strip()]
        if not lines:
            return False
        last = lines[-1].lstrip('﻿')
        return not (last.startswith(END_TEST_MARKER) or last.startswith('Время;'))

    def _convert_old_files(self):
        """Однократно добавляет BOM в старые файлы архива (записанные в UTF-8 без BOM)"""
        if not ARCHIVE_DIR.exists():
            return
        for path in ARCHIVE_DIR.glob('*.csv'):
            try:
                with open(path, 'rb') as f:
                    if f.read(3) == BOM:
                        continue
                content = path.read_bytes()
                tmp = path.with_suffix('.csv.tmp')
                tmp.write_bytes(BOM + content)
                tmp.replace(path)
                self.logger.info(f'Архив: {path.name} перекодирован в UTF-8 с BOM')
            except PermissionError:
                self.logger.warning(f'Архив: {path.name} занят, перекодировка при следующем запуске')
            except Exception as e:
                self.logger.error(f'Архив: ошибка перекодировки {path.name} - {e}')

    # --- формат записи ---------------------------------------------------------------

    @staticmethod
    def _clean_text(value) -> str:
        # ';' и переводы строк в текстовых полях сдвигают колонки CSV
        return str(value).replace(';', ',').replace('\n', ' ').replace('\r', ' ')

    @staticmethod
    def _num(value) -> str:
        return str(float(value)).replace('.', ',')

    def _join_values(self, data: list) -> str:
        # Числа приводятся к float явно: в numpy 2 str() списка из np.float64
        # даёт 'np.float64(1.5)' вместо '1.5', и архив становится нечитаемым
        return ';'.join(x.replace('.', ',') if isinstance(x, str) else self._num(x) for x in data)

    def _format_test(self, obj: dict) -> str:
        amort = obj['amort']
        time_t = datetime.now().strftime('%H:%M:%S')

        write_name = (f'{time_t};'
                      f'{self._clean_text(obj["operator_name"])};'
                      f'{self._clean_text(obj["operator_rank"])};'
                      f'{obj["type_test"]};'
                      f'{self._clean_text(amort.name)};'
                      f'{self._clean_text(obj["serial"])};')

        write_str = (f'{amort.min_length};'
                     f'{amort.max_length};'
                     f'{amort.hod};'
                     f'{amort.speed_one};'
                     f'{amort.min_recoil};'
                     f'{amort.max_recoil};'
                     f'{amort.min_comp};'
                     f'{amort.max_comp};'
                     f'{amort.speed_two};'
                     f'{amort.min_recoil_2};'
                     f'{amort.max_recoil_2};'
                     f'{amort.min_comp_2};'
                     f'{amort.max_comp_2};'
                     f'{obj["flag_push_force"]};'
                     f'{obj["static_push_force"]};'
                     f'{obj["dynamic_push_force"]};'
                     f'{obj["max_temperature"]};').replace('.', ',')

        speed = str(obj['speed']).replace('.', ',')

        if obj['type_test'] == 'temper':
            data_first = self._join_values(obj['temper_graph'])
            temper_force = [f'{float(r)}|{float(c)}'
                            for r, c in zip(obj['temper_recoil_graph'], obj['temper_comp_graph'])]
            data_second = self._join_values(temper_force)
        else:
            data_first = self._join_values(obj['move_graph'])
            data_second = self._join_values(obj['force_graph'])

        return (write_name + write_str +
                f'{speed};{data_first};\n'
                f'*;;;;;;;;;;;;;;;;;;;;;;;;{data_second};\n')
