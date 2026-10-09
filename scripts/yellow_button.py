# -*- coding: utf-8 -*-
import time

from scripts.logger import my_logger


class YellowButton:
    """
    Распознавание нажатия жёлтой кнопки (SB3, бит 13 регистра состояния).

    Срабатывание - по факту нажатия (переход из «отпущено»), а не по уровню:
    одно нажатие = одно событие, сколько бы кнопку ни держали.

    Состояние приходит из двух источников - чтение регистров ('reg') и записи
    буфера ('buffer'). В одной из прошивок бит кнопки в буфере приходил
    инвертированным, поэтому уровень «отпущено» не задаётся жёстко, а выясняется
    для каждого источника заново после переключения: уровень, державшийся
    IDLE_LEARN секунд, считается «отпущено». Если «отпущено» = 1, пишется
    предупреждение в лог (признак инвертированного бита).
    """
    IDLE_LEARN = 0.5    # сколько уровень должен держаться, чтобы считаться «отпущено», с
    DEBOUNCE = 0.1      # защита от дребезга контактов, с
    LOCKOUT = 1.5       # минимальный интервал между срабатываниями, с

    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self._source = None
        self._idle = None           # уровень «отпущено» для текущего источника
        self._level = None          # последний полученный уровень
        self._level_since = 0.0     # с какого момента держится этот уровень
        self._pressed = False       # нажатие уже засчитано, ждём отпускания
        self._last_event = -1e9
        self._warned_inverted: set[str] = set()

    def update(self, level, source: str, now: float | None = None) -> bool:
        """Новое состояние бита кнопки. True - зафиксировано нажатие"""
        now = time.monotonic() if now is None else now
        level = bool(level)

        if source != self._source:
            # другой источник - полярность может отличаться, выясняем заново
            self._source = source
            self._idle = None
            self._pressed = False
            self._level = level
            self._level_since = now
            return False

        if level != self._level:
            self._level = level
            self._level_since = now
        stable = now - self._level_since

        if self._idle is None:
            if stable >= self.IDLE_LEARN:
                self._idle = level
                if level and source not in self._warned_inverted:
                    self._warned_inverted.add(source)
                    self.logger.warning(f'Жёлтая кнопка: в источнике "{source}" бит 13 в отпущенном '
                                        f'состоянии = 1 (инвертирован относительно документации)')
            return False

        if not self._pressed:
            if level != self._idle and stable >= self.DEBOUNCE and now - self._last_event >= self.LOCKOUT:
                self._pressed = True
                self._last_event = now
                return True
        elif level == self._idle and stable >= self.DEBOUNCE:
            self._pressed = False
        return False
