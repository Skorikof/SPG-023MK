import serial
import serial.rs485
import struct
import threading
import queue
import time
from enum import Enum

from scripts.parser.parser import ParserSPG023MK


class ReadMode(Enum):
    FAST = 1
    BUFFER = 2
    

def modbus_crc(data: bytes) -> bytes:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little')


class RS485Port:
    def __init__(self, port: str, baudrate: int):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=0.02,
            bytesize=8,
            parity='N',
            stopbits=1
        )

        self.ser.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx=True,
            rts_level_for_rx=False
        )

        self.lock = threading.Lock()

    def open(self):
        if not self.ser.is_open:
            self.ser.open()

    def write(self, data: bytes):
        with self.lock:
            self.ser.write(data)
            self.ser.flush()

    def read(self, size: int) -> bytes:
        return self.ser.read(size)


class ModbusWorker(threading.Thread):
    def __init__(self, port: RS485Port, slave_id: int):
        super().__init__(daemon=True)
        self.port = port
        self.slave_id = slave_id
        self.queue = queue.PriorityQueue()
        self.running = True

    def run(self):
        while self.running:
            try:
                prio, frame, resp_len, cb = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue

            self.port.write(frame)
            resp = self.port.read(resp_len)

            if cb:
                cb(resp)

            time.sleep(0.001)  # пауза между кадрами

    def stop(self):
        self.running = False

    def send(self, frame, resp_len, callback=None, priority=5):
        self.queue.put((priority, frame, resp_len, callback))


class ModbusRTUMaster:
    def __init__(self, worker: ModbusWorker):
        self.w = worker
        self.sid = worker.slave_id

    def read_holding(self, addr, count, cb, prio=5):
        frame = bytearray([
            self.sid, 0x03,
            addr >> 8, addr & 0xFF,
            count >> 8, count & 0xFF
        ])
        frame += modbus_crc(frame)

        self.w.send(frame, 5 + count * 2, cb, prio)

    def write_regs(self, addr, values, prio=0):
        cnt = len(values)
        frame = bytearray([
            self.sid, 0x10,
            addr >> 8, addr & 0xFF,
            cnt >> 8, cnt & 0xFF,
            cnt * 2
        ])
        for v in values:
            frame += bytes([v >> 8, v & 0xFF])
        frame += modbus_crc(frame)

        self.w.send(frame, 8, None, prio)


class SPG007MKController:
    # --- адреса ---
    FAST_ADDR = 0x2000
    FAST_COUNT = 14

    BUF_START = 0x4000
    RECORD_SIZE = 6
    RECORD_COUNT = 3000

    def __init__(self, port: str, baudrate: int):
        self.port = RS485Port(port, baudrate)
        self.worker = ModbusWorker(self.port, slave_id=1)
        self.modbus = ModbusRTUMaster(self.worker)
        self.mode = ReadMode.FAST
        self.mode_lock = threading.Lock()
        self.parser = ParserSPG023MK()

        self.on_fast_data = None
        self.on_record = None
        self.last_record = None
        self.running = False
        self.fast_status = {}
        
    # --- UI callbacks ---
    def ui_start_buffer_read(self):
        self.set_mode(ReadMode.BUFFER)

    def ui_stop_buffer_read(self):
        self.set_mode(ReadMode.FAST)

    def ui_write_registers(self, addr, values):
        self.modbus.write_regs(addr, values, prio=0)

    # ---------- lifecycle ----------
    def start(self):
        self.port.open()
        self.worker.start()
        self.running = True
        self.mode = ReadMode.FAST
        self._start_reader()

    def stop(self):
        self.running = False
        self.worker.stop()
        
    def set_mode(self, mode: ReadMode):
        with self.mode_lock:
            self.mode = mode
            
    def _start_reader(self):
        def loop():
            while self.running:
                with self.mode_lock:
                    mode = self.mode

                if mode == ReadMode.FAST:
                    if self.worker.queue.qsize() < 5:
                        self._read_fast()
                    time.sleep(0.05)

                elif mode == ReadMode.BUFFER:
                    if self.worker.queue.qsize() < 10:
                        self._read_buffer_step()
                    time.sleep(0.0015)

        threading.Thread(target=loop, daemon=True).start()

    def _read_fast(self):
        self.modbus.read_holding(
            self.FAST_ADDR,
            self.FAST_COUNT,
            self._on_fast,
            prio=1
        )

    def _on_fast(self, resp: bytes):
        if resp != b'':
            regs = self.parse_fc03(resp, self.FAST_COUNT)
            if regs is None:
                return

            self.fast_status = {
                "force": self.parser.magnitude_effort(regs[0], regs[1]),
                "pos": self.parser.movement_amount(regs[2]),
                "state": self.parser.register_state(regs[3]),
                "state_list": self.parser.change_state_list(regs[3]),
                "time_ms": self.parser.counter_time(regs[4]),
                "switch": self.parser.switch_state(regs[5]),
                "traverse": round(0.5 * self.parser.movement_amount(regs[6]), 1),
                "first_t": self.parser.temperature_value(regs[7], regs[8]),
                "force_a": self.parser.emergency_force(regs[10], regs[11]),
                "second_t": self.parser.temperature_value(regs[12], regs[13])
            }

        if self.on_fast_data:
            self.on_fast_data(self.fast_status)
        
    def parse_fc03(self, resp, expected_regs):
        if len(resp) < 5:
            return None

        if resp[1] & 0x80:
            code = resp[2]
            print(f"⚠ Modbus exception {code}")
            return None

        byte_count = resp[2]
        if byte_count != expected_regs * 2:
            print("⚠ Unexpected byte count")
            return None

        if modbus_crc(resp[:-2]) != resp[-2:]:
            print("⚠ CRC error")
            return None

        data = resp[3:-2]
        return [(data[i] << 8) | data[i+1] for i in range(0, len(data), 2)]

    # ---------- data buffer ----------
    def _read_buffer_step(self):
        addr = self.BUF_START
        if self.last_record is not None:
            addr += (self.last_record % self.RECORD_COUNT) * self.RECORD_SIZE

        self.modbus.read_holding(
            addr,
            self.RECORD_SIZE,
            self._on_record,
            prio=5
        )
        
    def _on_record(self, resp: bytes):
        data = resp[3:-2]
        r = [(data[i] << 8) | data[i+1] for i in range(0, len(data), 2)]
        num = r[0]

        if self.last_record is None:
            self.last_record = num
            return

        if num == self.last_record:
            # буфер дочитан → возвращаемся
            self.set_mode(ReadMode.FAST)
            return

        self.last_record = num

        self.on_record({
            "num": num,
            "force": self.parser.magnitude_effort(r[1], r[2]),
            "pos": self.parser.movement_amount(r[3]),
            "state": self.parser.register_state(r[4]),
            "temp": self.parser.temperature_value(r[5], r[6])
        })

    # ---------- API ----------
    def on_record(self, record: dict):
        if self.on_record:
            self.on_record(record)

    def set_emergency_force(self, value: float):
        hi, lo = struct.unpack(">HH", struct.pack(">f", value))
        self.modbus.write_regs(0x200A, [hi, lo])


if __name__ == "__main__":
    ctrl = SPG007MKController('COM4')
    ctrl.start()

    time.sleep(30)

    ctrl.stop()

    # UI callbacks example:
    # buttonStart.clicked.connect(ctrl.ui_start_buffer_read)
    # buttonStop.clicked.connect(ctrl.ui_stop_buffer_read)
    # buttonWrite.clicked.connect(
    #     lambda: ctrl.ui_write_registers(0x200A, [hi, lo])
    # )
