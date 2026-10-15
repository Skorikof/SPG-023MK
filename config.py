# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
    
    @property
    def comport(self) -> str:
        return os.getenv("COM", "COM1")
    
    @property
    def baudrate(self) -> int:
        return int(os.getenv("BAUDRATE", "460800"))
    
    @property
    def timeout(self) -> float:
        return float(os.getenv("TIMEOUT", "0.02"))
    
    @property
    def retries(self) -> int:
        return int(os.getenv("RETRIES", "1"))

    @property
    def pause_reg(self) -> float:
        return float(os.getenv("PAUSE_REG", "0.05"))
    
    @property
    def pause_buf(self) -> float:
        return float(os.getenv("PAUSE_BUF", "0.01"))
    
    @property
    def pause_write(self) -> float:
        return float(os.getenv("PAUSE_WRITE", "0.005"))
    
    @property
    def const_traverse(self) -> int:
        return int(os.getenv("CONST_TRAV", "760"))
    
    @property
    def freq_select(self) -> str:
        return os.getenv("FREQ", "E")
    
    @property
    def log_level(self) -> int:
        return int(os.getenv("LOG_LEVEL", "20"))
    
    @property
    def force_koef(self) -> float:
        return float(os.getenv("FORCE_KOEF", "1"))
    
    @property
    def finish_temper(self) -> int:
        return int(os.getenv("FINISH_TEMPER", "80"))

    @property
    def buffer_timeout(self) -> float:
        """Страховка буфера: сколько секунд без новых данных из буфера считать сбоем
        (буфер пишет запись каждую 1 мс, пока включён), после чего буфер перезапускается"""
        return float(os.getenv("BUFFER_TIMEOUT", "5"))

    @property
    def buffer_restarts(self) -> int:
        """Страховка буфера: сколько перезапусков подряд без данных, затем авария (стоп привода)"""
        return int(os.getenv("BUFFER_RESTARTS", "3"))

    @property
    def speed_tolerance(self) -> float:
        """Допуск набора скорости испытания, %: сбор начинается, когда фактическая скорость
        (π * ход / период оборота) два оборота подряд в этом допуске от заданной"""
        return float(os.getenv("SPEED_TOLERANCE", "5"))

    @property
    def speed_wait_cycles(self) -> int:
        """Сколько оборотов ждать набора скорости; дальше сбор идёт как есть,
        а оператор в конце испытания получает сообщение с фактической скоростью"""
        return int(os.getenv("SPEED_WAIT_CYCLES", "10"))

    @property
    def alarm_filter_reads(self) -> int:
        """Фильтр аварий от помех: концевик траверсы, ограждение и перегрев засчитываются,
        если сигнал держится столько чтений подряд (одно чтение - примерно 20-50 мс).
        TRAVERSE_ALARM_READS - прежнее имя настройки"""
        return int(os.getenv("ALARM_FILTER_READS", os.getenv("TRAVERSE_ALARM_READS", "3")))

    @property
    def alarm_filter_ms(self) -> float:
        """Фильтр аварий от помех по времени: концевик траверсы, ограждение и перегрев
        засчитываются, если сигнал держится не меньше стольких миллисекунд (и не меньше
        ALARM_FILTER_READS чтений). Чтение регистров идёт каждые несколько мс, поэтому
        одних 3 чтений мало против дребезга концевика от вибрации на высокой скорости"""
        return float(os.getenv("ALARM_FILTER_MS", "200"))

    @property
    def buffer_dump(self) -> bool:
        """Диагностика: запись сырого потока буфера и событий обмена в logs/buffer/
        (файл на операцию стенда, разбор - tools/buffer_dump). 1 - включено"""
        return os.getenv("BUFFER_DUMP", "0").strip() not in ("", "0")

    @property
    def mid_lead(self) -> float:
        """Упреждение остановки в середине хода (настройка хода), мм: команда «стоп»
        подаётся на столько раньше середины, чтобы шатун выбегом дошёл до неё.
        13 - измеренный выбег на стенде при ходе 100 (медленная скорость 0.02 м/с)"""
        return float(os.getenv("MID_LEAD", "13"))
    
config = Config()
