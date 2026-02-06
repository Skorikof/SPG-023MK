from dataclasses import dataclass, field
from enum import Enum
import itertools
import math
import serial
import serial.rs485
import struct
import threading
import queue
import time

from scripts.parser.parser import ParserSPG023MK
from scripts.data_classes import FastStatus


class ReadMode(Enum):
    FAST = 1
    BUFFER = 2
    

class StateBits(Enum):
    BIT_CYCLE_FORCE = 0
    BIT_RED_LIGHT = 1
    BIT_GREEN_LIGHT = 2
    BIT_LOST_CONTROL = 3
    BIT_EXCESS_FORCE = 4
    BIT_SELECT_TEMPER = 6
    

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
        self._seq = itertools.count()

    def run(self):
        while self.running:
            try:
                prio, seq, frame, resp_len, cb = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                self.port.write(frame)
                resp = self.port.read(resp_len)

                if cb:
                    cb(resp)

            except Exception as e:
                print(f"ModbusWorker error: {e}")

            time.sleep(0.001)  # пауза между кадрами

    def stop(self):
        self.running = False

    def send(self, frame, resp_len, callback=None, priority=5):
        self.queue.put((
            priority,
            next(self._seq),
            frame,
            resp_len,
            callback
        ))


class ModbusRTUMaster:
    def __init__(self, worker: ModbusWorker):
        self.w = worker
        self.sid = worker.slave_id

    def read_holding(self, addr: int, count: int, cb, *, prio: int = 1):
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
    
    STATE_REG = 0x2003

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
        
        self.fast_status = FastStatus()
        self.on_fast_data = None
        self.on_record = None
        self.last_record = None
        self.running = False
        self.buf_addr = self.BUF_START
        self.last_record = None
        self.buffer_active = False
        self.missed_records = 0
        self.on_missed_records = None
        self._last_emergency_force = None
        
        self.on_error = None

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
                    time.sleep(0.001)

        threading.Thread(target=loop, daemon=True).start()

    def _read_fast(self):
        self.modbus.read_holding(
            self.FAST_ADDR,
            self.FAST_COUNT,
            self._on_fast,
            prio=1
        )

    def _on_fast(self, resp: bytes):
        regs = self.parse_fc03(resp, self.FAST_COUNT)
        if regs is None:
            return
        force = self.parser.parse_float(regs[0], regs[1])
        pos = self.parser.movement_amount(regs[2], 'pos')
        state = self.parser.register_state(regs[3])
        switch = self.parser.switch_state(regs[5])
        traverse = self.parser.movement_amount(regs[6], 'traverse')
        first_t = self.parser.parse_float(regs[7], regs[8])
        force_a = self.parser.parse_float(regs[10], regs[11])
        second_t = self.parser.parse_float(regs[12], regs[13])

        values = (force, pos, state, switch, traverse, first_t, force_a, second_t)
        if any(v is None for v in values):
            return

        self.fast_status = FastStatus(
            force=force,
            pos=pos,
            state=state,
            time_ms=regs[4],
            switch=switch,
            traverse=traverse,
            first_t=first_t,
            force_a=force_a,
            second_t=second_t,
            )

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
    def ui_start_buffer_read(self):
        self.buffer_active = True
        self.last_record = None
        self.buf_addr = self.BUF_START
        self.set_mode(ReadMode.BUFFER)
        
    def ui_stop_buffer_read(self):
        self.buffer_active = False
        self.set_mode(ReadMode.FAST)
    
    def _read_buffer_step(self):
        if not self.buffer_active:
            return

        self.modbus.read_holding(
            self.buf_addr,
            self.RECORD_SIZE,
            self._on_record,
            prio=5
        )
        
    def _on_record(self, resp: bytes):
        regs = self.parse_fc03(resp, self.RECORD_SIZE)
        if regs is None:
            return

        rec_id = regs[0]

        if self.last_record is None:
            # первая валидная запись после старта
            self.last_record = rec_id
            self._emit_record(regs)
            self._advance_buf_addr()
            return

        delta = rec_id - self.last_record

        if delta <= 0:
            # либо ещё не перезаписано, либо мы слишком рано читаем
            return

        if delta > 1:
            self.missed_records += delta - 1
            
            if self.on_missed_records and self.missed_records % 10 == 0:
                self.on_missed_records(self.missed_records)

        self.last_record = rec_id
        self._emit_record(regs)
        self._advance_buf_addr()
        
    def _advance_buf_addr(self):
        self.buf_addr += self.RECORD_SIZE
        if self.buf_addr > (self.BUF_START + self.RECORD_SIZE * self.RECORD_COUNT - 1):
            self.buf_addr = self.BUF_START
            
    def _emit_record(self, regs):
        if not self.on_record:
            return

        self.on_record({
            "num": regs[0],
            "force": self.parser.parse_float(regs[1], regs[2]),
            "pos": self.parser.movement_amount(regs[3]),
            "state": self.parser.register_state(regs[4]),
            "temp": self.parser.parse_float(regs[5], regs[6])
        })
        
    def _float_to_regs(self, value: float) -> tuple[int, int]:
        return struct.unpack('>HH', struct.pack('>f', value))
    
    def _modify_state_reg(self, updates: dict[int, bool]):
        """Запись битов в регистр состояния 0х2003"""
        def on_read(resp: bytes):
            regs = self.parse_fc03(resp, 1)
            if not regs:
                return

            value = regs[0]

            for bit, flag in updates.items():
                if flag:
                    value |= (1 << bit)
                else:
                    value &= ~(1 << bit)

            self.modbus.write_regs(
                addr=self.STATE_REG,
                values=[value],
                prio=0
            )

        self.modbus.read_holding(self.STATE_REG, 1, on_read, prio=0)

    # ---------- API ----------
    def set_emergency_force(self, value: float):
        """Запись аварийного усилия (float32) в регистры 0x200A–0x200B"""
        if not math.isfinite(value):
            raise ValueError("Emergency force must be finite")
        
        if value == self._last_emergency_force:
            return
        self._last_emergency_force = value

        try:
            hi, lo = struct.unpack('>HH', struct.pack('>f', value))
            self.modbus.write_regs(0x200A, [hi, lo], prio=0)
        except Exception as e:
            self.on_error(f"Error setting emergency force: {e}")
            raise
        
    def set_cycle_force(self, enable: bool):
        self._modify_state_reg({
            StateBits.BIT_CYCLE_FORCE: enable
        })
        
    def set_red_light(self, enable: bool):
        self._modify_state_reg({
            StateBits.BIT_RED_LIGHT: enable
        })
        
    def set_green_light(self, enable: bool):
        self._modify_state_reg({
            StateBits.BIT_GREEN_LIGHT: enable
        })
        
    def set_unblock_control(self):
        self._modify_state_reg({
            StateBits.BIT_LOST_CONTROL: True
        })
        
    def set_unblock_excess_force(self):
        self._modify_state_reg({
            StateBits.BIT_EXCESS_FORCE: True
        })
        
    def set_select_temper(self, enable: bool):
        self._modify_state_reg({
            StateBits.BIT_SELECT_TEMPER: enable
        })


if __name__ == "__main__":
    ctrl = SPG007MKController('COM4')
    ctrl.start()
    time.sleep(10)
    ctrl.stop()
