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
        а если и собранный оборот вне допуска - WARNING в логе с фактической скоростью"""
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
    def traverse_alarm_ms(self) -> float:
        """Аварийные концевики траверсы засчитываются, если сигнал держится столько мс.
        Настоящий концевик механически запирает траверсу - сигнал держится, пока оператор её
        не выведет; помехи входа 0x2005 - до 250 мс (19.10)"""
        return float(os.getenv("TRAVERSE_ALARM_MS", "1000"))

    @property
    def collect_stable_pct(self) -> float:
        """Стабильность оборотов при сборе результата: два последних оборота шага должны
        совпасть по отбою и сжатию в пределах стольких %, иначе собирается следующий.
        0 - проверка выключена (как раньше: последний из двух). Обычный разброс соседних
        оборотов (16-21.10) - медиана 0.2-1.2 %, 95 % пар - до 2.3 %"""
        return float(os.getenv("COLLECT_STABLE_PCT", "5"))

    @property
    def collect_stable_cycles(self) -> int:
        """Сколько последних оборотов подряд должны совпасть (не меньше 2). Двух мало:
        «провал» отбоя бывает два оборота подряд (21.10, 0.8 м/с: 327, 173, 180 кгс);
        каждый лишний оборот удлиняет шаг на период оборота (0.02 м/с, ход 100 - 16 с)"""
        return int(os.getenv("COLLECT_STABLE_CYCLES", "3"))

    @property
    def collect_stable_min_kgf(self) -> float:
        """...но не меньше стольких кгс: на малых скоростях усилия единицы кгс, и проценты
        от них меньше шума датчика (до 0.8 кгс)"""
        return float(os.getenv("COLLECT_STABLE_MIN_KGF", "1"))

    @property
    def collect_max_cycles(self) -> int:
        """Сколько оборотов собирать на шаге не больше; не совпали - в результат оборот с
        наибольшим усилием (отбой + сжатие), WARNING в логе"""
        return int(os.getenv("COLLECT_MAX_CYCLES", "6"))

    @property
    def speed_slip(self) -> float:
        """Поправка на скольжение в пересчёте скорости испытания в частоту ЧП (частота делится
        на неё). 1.0 - ЧП сам компенсирует скольжение (так по записям 16-21.10); 0.98 - как
        было до 21.10 (все скорости на +2 % выше заданной)"""
        return float(os.getenv("SPEED_SLIP", "1.0"))

    @property
    def speed_freq_offset_hz(self) -> float:
        """Постоянная добавка частоты ЧП, Гц: по записям 16-21.10 двигатель вращается так,
        будто частота на ≈ 0.14 Гц выше заданной (на 0.02 м/с это +6 % скорости). Вычитается
        из частоты команды; 0 - не учитывать"""
        return float(os.getenv("SPEED_FREQ_OFFSET_HZ", "0.14"))

    @property
    def turn_hyst_mm(self) -> float:
        """Развороты шатуна по положению: разворот засчитывается, когда шатун отошёл от
        экстремума на столько мм (шум линейки ±0.1 мм). 0 - старое определение по знаку
        скорости (терял развороты - двойные петли)"""
        return float(os.getenv("TURN_HYST_MM", "1.0"))

    @property
    def stop_window_ms(self) -> int:
        """Остановка шатуна (ЧП закончил торможение): за столько мс (записей буфера)..."""
        return int(os.getenv("STOP_WINDOW_MS", "500"))

    @property
    def stop_span_mm(self) -> float:
        """...положение сдвинулось не больше чем на столько мм. Не 0: после торможения шатун
        может ползти 2-3 мм/с под действием амортизатора десятки секунд (19.10, ход 100),
        для доводки до НМТ (20 мм/с) это уже не движение"""
        return float(os.getenv("STOP_SPAN_MM", "2.0"))

    @property
    def stop_timeout(self) -> float:
        """Шатун не остановился за столько секунд после команды «стоп» - команда повторяется
        (WARNING в логе)"""
        return float(os.getenv("STOP_TIMEOUT", "10"))

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
