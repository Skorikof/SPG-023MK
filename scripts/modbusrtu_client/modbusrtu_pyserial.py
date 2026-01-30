import time
import serial


class OptimizedPySerialExample:
    """Оптимизированный пример PySerial для максимальной производительности"""
    
    def __init__(self):
        self.serial = None
        self.crc_cache = {}  # Кэш CRC для часто используемых запросов
        self.request_template = bytearray(256)  # Предварительно выделенный буфер
        
    def connect(self, port='COM4', baudrate=460800):
        """Подключение с оптимизированными параметрами"""
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=0.1,          # Минимальный безопасный таймаут
            inter_byte_timeout=0.002, # Агрессивный таймаут между байтами
            write_timeout=0.1,
            exclusive=True         # Эксклюзивный доступ к порту
        )
    
    def fast_crc16(self, data: bytes) -> int:
        """Оптимизированный расчет CRC16 с lookup таблицей"""
        if not hasattr(self, '_crc_table'):
            # Создаем lookup таблицу один раз
            self._crc_table = []
            for i in range(256):
                crc = i
                for _ in range(8):
                    if crc & 0x0001:
                        crc = (crc >> 1) ^ 0xA001
                    else:
                        crc >>= 1
                self._crc_table.append(crc)
        
        crc = 0xFFFF
        for byte in data:
            crc = (crc >> 8) ^ self._crc_table[(crc ^ byte) & 0xFF]
        return crc
    
    def build_optimized_request(self, slave_id: int, address: int, count: int) -> bytes:
        """Оптимизированное построение запроса с кэшированием"""
        cache_key = (slave_id, address, count)
        
        if cache_key in self.crc_cache:
            return self.crc_cache[cache_key]
        
        # Используем предварительно выделенный буфер
        buf = self.request_template
        buf[0] = slave_id
        buf[1] = 0x03  # функция чтения регистров
        buf[2] = (address >> 8) & 0xFF
        buf[3] = address & 0xFF
        buf[4] = (count >> 8) & 0xFF
        buf[5] = count & 0xFF
        
        # Рассчитываем CRC
        crc = self.fast_crc16(buf[:6])
        buf[6] = crc & 0xFF
        buf[7] = (crc >> 8) & 0xFF
        
        # Сохраняем в кэш
        result = bytes(buf[:8])
        self.crc_cache[cache_key] = result
        
        return result
    
    def read_registers_fast(self, slave_id: int, address: int, count: int, retries: int = 2):
        """Оптимизированное чтение регистров"""
        request = self.build_optimized_request(slave_id, address, count)
        expected_len = 5 + count * 2
        
        for attempt in range(retries):
            try:                
                # Отправляем запрос
                # start_write = time.perf_counter()
                self.serial.write(request)
                self.serial.flush()
                # write_time = time.perf_counter() - start_write
                
                # Читаем ответ
                response = bytearray()
                # read_start = time.time()
                
                while len(response) < expected_len:
                    # Агрессивное чтение с минимальными задержками
                    # timeout = 0.025 - (time.time() - read_start)
                    # if timeout <= 0:
                    #     break
                    
                    # self.serial.timeout = min(timeout, 0.001)
                    chunk = self.serial.read(expected_len - len(response))
                    if chunk:
                        response.extend(chunk)
                    else:
                        time.sleep(0.0001)  # 100 микросекунд
                
                if len(response) == expected_len:
                    # Быстрая проверка CRC
                    if self.fast_crc16(response[:-2]) == ((response[-1] << 8) | response[-2]):
                        # Быстрый парсинг данных
                        # registers = ()
                        for i in range(3, 3 + count * 2, 2):
                            registers = ((response[i] << 8) | response[i + 1])
                        return registers
                
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                time.sleep(0.001 * (attempt + 1))
        
        return None
    
    def bulk_read_optimized(self, requests: list):
        """Пакетное чтение с минимальными накладными расходами"""
        results = []
        
        # Группируем запросы по slave_id для минимизации переключений
        requests_by_slave = {}
        for slave_id, address, count in requests:
            if slave_id not in requests_by_slave:
                requests_by_slave[slave_id] = []
            requests_by_slave[slave_id].append((address, count))
        
        for slave_id, slave_requests in requests_by_slave.items():
            # Сортируем по адресу для возможной оптимизации
            slave_requests.sort(key=lambda x: x[0])
            
            for address, count in slave_requests:
                result = self.read_registers_fast(slave_id, address, count)
                results.append(result)
        
        return results


if __name__ == "__main__":
    client = OptimizedPySerialExample()
    client.connect()
    for i in range(100):
        print(client.read_registers_fast(1, 8198, 1))
