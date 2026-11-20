# -*- coding: utf-8 -*-
from PySide6.QtCore import QObject, QEvent, Qt, QTimer
from PySide6.QtWidgets import QComboBox, QCompleter


class SearchCombo(QObject):
    """
    Поиск в выпадающем списке: в поле можно вводить часть текста (в любом месте, без
    учёта регистра) - выпадает список совпадений. Выбор из него, Enter с точным текстом
    пункта или стрелка списка - как обычный выбор: вызывается on_select(индекс). Если ввод
    не совпал ни с одним пунктом, при уходе из поля возвращается текст выбранного пункта.
    Щелчок в поле выделяет текст - ввод сразу его заменяет.

    Пункты списка добавляются как обычно (clear/addItems) - поиск идёт по текущим пунктам
    """
    def __init__(self, combo: QComboBox, on_select, max_visible: int = 15):
        super().__init__(combo)
        self.combo = combo
        self.on_select = on_select

        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        # поле ввода, появившееся у списка, шрифт списка не наследует, если у списка задан
        # стиль (цвет фона) - текст становился системным ~9 pt вместо шрифта формы
        combo.lineEdit().setFont(combo.font())
        completer = combo.completer()
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setMaxVisibleItems(max_visible)
        completer.popup().setFont(combo.font())
        completer.activated[str].connect(self._selected)
        combo.lineEdit().editingFinished.connect(self._finished)
        combo.lineEdit().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusIn:
            QTimer.singleShot(0, obj.selectAll)
        return super().eventFilter(obj, event)

    def _select(self, ind: int):
        self.combo.setCurrentIndex(ind)
        self.on_select(ind)

    def _selected(self, text: str):
        """Выбор из списка совпадений"""
        ind = self.combo.findText(text, Qt.MatchFlag.MatchExactly)
        if ind >= 0:
            self._select(ind)

    def _finished(self):
        """Ввод закончен: точный текст пункта (без учёта регистра) - выбрать его,
        иначе вернуть текст выбранного пункта"""
        combo = self.combo
        if combo.count() == 0:
            return
        text = combo.currentText().strip()
        cur = combo.currentIndex()
        if cur >= 0 and combo.itemText(cur) == text:
            return
        ind = combo.findText(text, Qt.MatchFlag.MatchFixedString)
        if ind >= 0:
            self._select(ind)
        else:
            combo.setEditText(combo.itemText(cur) if cur >= 0 else '')
