import serial
import struct
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass
from threading import Lock

# from logger import my_logger


@dataclass
class ModbusDevice:
    """Конфигурация устройства Modbus"""
    slave_id: int
    description: str = ""
    response_timeout: float = 0.1
    retry_count: int = 3


class FastModbusRTU:
    """Высокопроизводительный Modbus RTU клиент на PySerial"""
    # Коды функций Modbus
    READ_COILS = 0x01
    READ_DISCRETE_INPUTS = 0x02
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_COIL = 0x05
    WRITE_SINGLE_REGISTER = 0x06
    WRITE_MULTIPLE_REGISTERS = 0x10
    
    def __init__(self, 
                 port: str = 'COM4',
                 baudrate: int = 460800,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: int = 1,
                 timeout: float = 0.1,
                 inter_byte_timeout: float = 0.01):
        """
        Инициализация Modbus RTU соединения
        Args:
            port: COM порт (например, 'COM3', '/dev/ttyUSB0')
            baudrate: Скорость передачи (9600, 19200, 38400, 57600, 115200)
            timeout: Таймаут чтения в секундах
            inter_byte_timeout: Таймаут между байтами
        """
        # self.logger = my_logger.get_logger(__name__)
        
        # Создаем блокировку для потокобезопасности
        self._lock = Lock()
        
        # Инициализируем последовательный порт
        self.serial = serial.Serial(port=port,
                                    baudrate=baudrate,
                                    bytesize=bytesize,
                                    parity=parity,
                                    stopbits=stopbits,
                                    timeout=timeout,
                                    inter_byte_timeout=inter_byte_timeout,
                                    rtscts=False,      # Не использовать аппаратное управление потоком
                                    dsrdtr=False,
                                    exclusive=True     # Эксклюзивный доступ к порту
                                )
        
        # Очищаем буферы
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        
        # Статистика производительности
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'total_time': 0.0
        }
        
        # self.logger.info(f"Modbus RTU инициализирован на {port} со скоростью {baudrate}")
    
    def crc16(self, data: bytes) -> int:
        """
        Быстрый расчет CRC16 для Modbus RTU (полином 0xA001)
        Args:
            data: Данные для расчета CRC
        Returns:
            CRC16 значение
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def _build_request(self, 
                      slave_id: int, 
                      function_code: int, 
                      data: bytes) -> bytes:
        """
        Построение Modbus запроса с CRC
        Args:
            slave_id: Адрес устройства
            function_code: Код функции Modbus
            data: Данные запроса
        Returns:
            Полный запрос с CRC
        """
        # Формируем заголовок запроса
        request = bytes([slave_id, function_code]) + data
        
        # Добавляем CRC (младший байт сначала)
        crc = self.crc16(request)
        request += struct.pack('<H', crc)  # Little-endian для CRC
        
        return request
    
    def _parse_response(self, 
                       response: bytes, 
                       slave_id: int, 
                       function_code: int) -> Tuple[bool, bytes]:
        """
        Парсинг ответа Modbus с проверкой CRC
        Args:
            response: Полный ответ от устройства
            slave_id: Ожидаемый адрес устройства
            function_code: Ожидаемый код функции
        Returns:
            (success, data) - успех и данные ответа
        """
        if len(response) < 5:  # Минимальный размер ответа
            # self.logger.error(f"Слишком короткий ответ: {len(response)} байт")
            return False, b''
        
        # Проверяем заголовок ответа
        if response[0] != slave_id:
            # self.logger.error(f"Неверный адрес устройства. Ожидалось {slave_id}, получено {response[0]}")
            return False, b''
        
        # Проверяем код функции
        if response[1] != function_code:
            # Проверка на исключение
            if response[1] == function_code | 0x80:
                error_code = response[2]
                error_messages = {
                    1: "Недопустимая функция",
                    2: "Недопустимый адрес",
                    3: "Недопустимое значение данных"
                }
                # self.logger.error(f"Ошибка устройства: {error_messages.get(error_code, f'Код {error_code}')}")
            else:
                # self.logger.error(f"Неверный код функции. Ожидалось {function_code}, получено {response[1]}")
                pass
            return False, b''
        
        # Проверяем CRC
        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = self.crc16(response[:-2])
        
        if received_crc != calculated_crc:
            # self.logger.error(f"Ошибка CRC. Получено: {received_crc:04X}, Рассчитано: {calculated_crc:04X}")
            return False, b''
        
        # Возвращаем данные (исключая заголовок и CRC)
        return True, response[3:-2]
    
    def _send_receive(self, 
                     request: bytes, 
                     expected_response_length: int,
                     device: ModbusDevice) -> Optional[bytes]:
        """
        Отправка запроса и получение ответа
        Args:
            request: Запрос для отправки
            expected_response_length: Ожидаемая длина ответа
            device: Конфигурация устройства
        Returns:
            Ответ от устройства или None при ошибке
        """
        start_time = time.perf_counter()
        
        with self._lock:  # Гарантируем потокобезопасность
            for attempt in range(device.retry_count):
                try:
                    # Очищаем буферы перед отправкой
                    self.serial.reset_input_buffer()
                    
                    # Отправляем запрос
                    self.serial.write(request)
                    self.serial.flush()  # Ждем отправки всех данных
                    
                    # Обновляем статистику
                    self.stats['total_bytes_sent'] += len(request)
                    
                    # Читаем ответ
                    response = bytearray()
                    bytes_to_read = expected_response_length
                    
                    # Читаем с таймаутом
                    read_start = time.time()
                    while len(response) < bytes_to_read:
                        if time.time() - read_start > device.response_timeout:
                            # self.logger.warning(f"Таймаут чтения для устройства {device.slave_id}")
                            break
                        
                        # Читаем доступные данные
                        available = self.serial.in_waiting
                        if available:
                            chunk = self.serial.read(min(available, bytes_to_read - len(response)))
                            response.extend(chunk)
                        else:
                            time.sleep(0.001)  # Короткая пауза
                    
                    # Если ответ слишком короткий, пытаемся прочитать еще
                    if len(response) < 5 and self.serial.in_waiting:
                        response.extend(self.serial.read(self.serial.in_waiting))
                    
                    elapsed = time.perf_counter() - start_time
                    self.stats['total_time'] += elapsed
                    
                    if response:
                        self.stats['total_bytes_received'] += len(response)
                        return bytes(response)
                    
                except serial.SerialException as e:
                    # self.logger.error(f"Ошибка порта при попытке {attempt + 1}: {e}")
                    if attempt == device.retry_count - 1:
                        return None
                    time.sleep(0.01 * (attempt + 1))  # Экспоненциальная задержка
        
        return None
    
    def read_holding_registers(self, 
                              device: ModbusDevice,
                              start_address: int,
                              register_count: int) -> Optional[List[int]]:
        """
        Чтение holding регистров (функция 03)
        Args:
            device: Устройство Modbus
            start_address: Начальный адрес регистра
            register_count: Количество регистров для чтения
        Returns:
            Список значений регистров или None при ошибке
        """
        self.stats['total_requests'] += 1
        
        # Формируем данные запроса
        data = struct.pack('>HH', start_address, register_count)
        
        # Строим запрос
        request = self._build_request(
            device.slave_id,
            self.READ_HOLDING_REGISTERS,
            data
        )
        
        # Ожидаемая длина ответа: 5 байт заголовка + 2*регистры + 2 CRC
        expected_length = 5 + register_count * 2
        
        # Отправляем и получаем ответ
        response = self._send_receive(request, expected_length, device)
        
        if not response:
            self.stats['failed_requests'] += 1
            return None
        
        # Парсим ответ
        success, response_data = self._parse_response(
            response, device.slave_id, self.READ_HOLDING_REGISTERS
        )
        
        if not success or len(response_data) < 2:
            self.stats['failed_requests'] += 1
            return None
        
        # Первый байт данных - количество байт в ответе
        byte_count = response_data[0]
        if byte_count != register_count * 2:
            pass
            # self.logger.warning(f"Неверное количество байт. Ожидалось {register_count*2}, получено {byte_count}")
        
        # Преобразуем байты в значения регистров
        registers = []
        for i in range(register_count):
            if (i * 2 + 2) <= len(response_data[1:]):
                value = struct.unpack('>H', response_data[1 + i*2: 1 + i*2 + 2])[0]
                registers.append(value)
        
        self.stats['successful_requests'] += 1
        return registers
    
    def write_single_register(self,
                             device: ModbusDevice,
                             address: int,
                             value: int) -> bool:
        """
        Запись одного регистра (функция 06)
        Args:
            device: Устройство Modbus
            address: Адрес регистра
            value: Значение для записи
        Returns:
            Успех операции
        """
        self.stats['total_requests'] += 1
        
        # Формируем данные запроса
        data = struct.pack('>HH', address, value)
        
        # Строим запрос
        request = self._build_request(
            device.slave_id,
            self.WRITE_SINGLE_REGISTER,
            data
        )
        
        # Ожидаемая длина ответа (эхо запроса)
        expected_length = 8
        
        # Отправляем и получаем ответ
        response = self._send_receive(request, expected_length, device)
        
        if not response:
            self.stats['failed_requests'] += 1
            return False
        
        # Парсим ответ (должен быть идентичен запросу)
        success, _ = self._parse_response(response, device.slave_id, self.WRITE_SINGLE_REGISTER)
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
            
        return success
    
    def bulk_read_registers(self,
                           devices: List[ModbusDevice],
                           start_address: int,
                           register_count: int) -> dict:
        """
        Массовое чтение регистров с нескольких устройств
        Args:
            devices: Список устройств
            start_address: Начальный адрес
            register_count: Количество регистров
            
        Returns:
            Словарь с результатами по каждому устройству
        """
        results = {}

        for device in devices:
            try:
                registers = self.read_holding_registers(device, start_address, register_count)
                results[device.slave_id] = {
                    'success': registers is not None,
                    'data': registers,
                    'timestamp': time.time()
                }
            except Exception as e:
                # self.logger.error(f"Ошибка чтения устройства {device.slave_id}: {e}")
                results[device.slave_id] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                }
        
        return results
    
    def get_statistics(self) -> dict:
        """
        Получение статистики производительности
        Returns:
            Словарь со статистикой
        """
        stats = self.stats.copy()
        if stats['total_requests'] > 0:
            stats['success_rate'] = (stats['successful_requests'] / stats['total_requests']) * 100
            stats['avg_request_time'] = stats['total_time'] / stats['total_requests']
            stats['throughput_bps'] = (stats['total_bytes_received'] * 8) / stats['total_time'] if stats['total_time'] > 0 else 0
        else:
            stats['success_rate'] = 0
            stats['avg_request_time'] = 0
            stats['throughput_bps'] = 0
            
        return stats
    
    def close(self):
        """Закрытие соединения"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            # self.logger.info("Modbus соединение закрыто")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class UltraFastModbusRTU(FastModbusRTU):
    """Ультра-быстрая версия с дополнительными оптимизациями"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Предварительно рассчитанные CRC для часто используемых запросов
        self.crc_cache = {}
        
        # Буферы для повторного использования
        self.request_buffer = bytearray(256)
        self.response_buffer = bytearray(512)
    
    def _build_request_cached(self, slave_id, function_code, address, count):
        """
        Построение запроса с использованием кэша CRC
        """
        cache_key = (slave_id, function_code, address, count)
        
        if cache_key in self.crc_cache:
            request, crc = self.crc_cache[cache_key]
            # Создаем новый запрос с кэшированным CRC
            full_request = request + struct.pack('<H', crc)
            return full_request
        
        # Формируем запрос
        request = struct.pack('>BBHH', slave_id, function_code, address, count)
        crc = self.crc16(request)
        
        # Кэшируем
        self.crc_cache[cache_key] = (request, crc)
        
        return request + struct.pack('<H', crc)
    
    def read_registers_burst(self, device, addresses_counts):
        """
        Пакетное чтение нескольких диапазонов регистров
        
        Args:
            device: Устройство
            addresses_counts: Список кортежей (адрес, количество)
            
        Returns:
            Словарь с результатами по каждому диапазону
        """
        results = {}
        
        with self._lock:
            for address, count in addresses_counts:
                request = self._build_request_cached(
                    device.slave_id,
                    self.READ_HOLDING_REGISTERS,
                    address,
                    count
                )
                
                # Используем предварительно выделенный буфер
                self.request_buffer[:len(request)] = request
                
                # Отправляем и читаем
                self.serial.write(self.request_buffer[:len(request)])
                
                # Быстрое чтение ответа
                expected_len = 5 + count * 2
                response = self.serial.read(expected_len)
                
                if len(response) == expected_len:
                    # Быстрая проверка CRC без создания новых объектов
                    crc_received = struct.unpack('<H', response[-2:])[0]
                    crc_calculated = self.crc16(response[:-2])
                    
                    if crc_received == crc_calculated:
                        # Парсинг данных
                        byte_count = response[2]
                        data = response[3:-2]
                        
                        registers = []
                        for i in range(0, byte_count, 2):
                            if i + 2 <= len(data):
                                value = (data[i] << 8) | data[i + 1]
                                registers.append(value)
                        
                        results[(address, count)] = registers
        
        return results


if __name__ == "__main__":
    client = UltraFastModbusRTU()
    device = ModbusDevice(1)
    
    for i in range(1_000_000):
        print(client.read_holding_registers(device, 8198, 1))
