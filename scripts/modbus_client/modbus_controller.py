from itertools import count
from PySide6.QtCore import QObject, Signal, Slot

from scripts.modbus_client.modbus_worker import SPG007MKController, ReadMode


class SPG005MKQtController(QObject):
    fastDataUpdated = Signal(object)
    bufferRecordReceived = Signal(object)
    errorOccurred = Signal(str)
    modeChanged = Signal(str)
    missedRecordsUpdated = Signal(int)

    def __init__(self, port: str, baudrate: int):
        super().__init__()
        self.ctrl = SPG007MKController(port, baudrate)

        self.ctrl.on_fast_data = self._emit_fast
        self.ctrl.on_record = self._emit_record
        self.ctrl.on_missed_records = self._emit_missed
        
    @Slot()
    def start(self):
        try:
            self.ctrl.start()
            self.modeChanged.emit("FAST")
        except Exception as e:
            self.errorOccurred.emit(str(e))

    @Slot()
    def stop(self):
        self.ctrl.stop()
        
    @Slot()
    def startBuffer(self):
        self.ctrl.set_mode(ReadMode.BUFFER)
        self.modeChanged.emit("BUFFER")

    @Slot()
    def stopBuffer(self):
        self.ctrl.set_mode(ReadMode.FAST)
        self.modeChanged.emit("FAST")
    
    @Slot(float)
    def setEmergencyForce(self, value: float):
        try:
            self.ctrl.set_emergency_force(value)
        except Exception as e:
            self.errorOccurred.emit(str(e))
    
    def _emit_fast(self, data: object):
        self.fastDataUpdated.emit(data)

    def _emit_record(self, record: object):
        self.bufferRecordReceived.emit(record)
        
    def _emit_missed(self, count: int):
        self.missedRecordsUpdated.emit(count)
