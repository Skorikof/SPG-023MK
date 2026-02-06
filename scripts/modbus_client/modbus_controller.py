from PySide6.QtCore import QObject, Signal, Slot

from scripts.modbus_client.modbus_worker import SPG007MKController, ReadMode


class SPG005MKQtController(QObject):
    fastDataUpdated = Signal(object)
    bufferRecordReceived = Signal(dict)
    errorOccurred = Signal(str)
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
        except Exception as e:
            self.errorOccurred.emit(str(e))

    @Slot()
    def stop(self):
        self.ctrl.stop()
        
    @Slot()
    def startBuffer(self):
        self.ctrl.ui_start_buffer_read()

    @Slot()
    def stopBuffer(self):
        self.ctrl.ui_stop_buffer_read()
    
    @Slot(float)
    def setEmergencyForce(self, value: float):
        try:
            self.ctrl.set_emergency_force(value)
        except Exception as e:
            self.errorOccurred.emit(f'Slot setEmergencyForce error: {e}')
            
    @Slot(bool)
    def setCycleForce(self, enble: bool):
        try:
            self.ctrl.set_cycle_force(enble)
        except Exception as e:
            self.errorOccurred.emit(f'Slot setCycleForce error: {e}')
            
    @Slot(bool)
    def setRedLight(self, enable: bool):
        try:
            self.ctrl.set_red_light(enable)
        except Exception as e:
            self.errorOccurred.emit(f'Slot setRedLight error: {e}')
            
    @Slot(bool)
    def setGreenLight(self, enable: bool):
        try:
            self.ctrl.set_green_light(enable)
        except Exception as e:
            self.errorOccurred.emit(f'Slot setGreenLight error: {e}')
            
    @Slot()
    def setUnblockControl(self):
        try:
            self.ctrl.set_unblock_control()
        except Exception as e:
            self.errorOccurred.emit(f'Slot setUnblockControl error: {e}')
            
    @Slot()
    def setUnblockExcessForce(self):
        try:
            self.ctrl.set_unblock_excess_force()
        except Exception as e:
            self.errorOccurred.emit(f'Slot setUnblockExcessForce error: {e}')
            
    @Slot(bool)
    def setSelectTemper(self, enable: bool):
        try:
            self.ctrl.set_select_temper(enable)
        except Exception as e:
            self.errorOccurred.emit(f'Slot setSelectTemper error: {e}')
            
    def _emit_fast(self, data: object):
        self.fastDataUpdated.emit(data)

    def _emit_record(self, record: dict):
        self.bufferRecordReceived.emit(record)
        
    def _emit_missed(self, count: int):
        self.missedRecordsUpdated.emit(count)
        
    def _emit_error(self, message: str):
        self.errorOccurred.emit(message)

