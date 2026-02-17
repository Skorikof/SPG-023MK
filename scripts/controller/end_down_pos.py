# import time
# import numpy as np
# from collections import deque


# class EndTestParkingController:
#     def __init__(self,
#                  read_position,
#                  set_freq,
#                  sample_rate=1000):

#         self.read_position = read_position
#         self.set_freq = set_freq
#         self.sample_rate = sample_rate

#         # параметры парковки
#         self.freq_down = -5.0     # % или Гц — зависит от твоего интерфейса
#         self.freq_up = 2.0
#         self.freq_zero = 0.0

#         # детектор минимума
#         self.prev_pos = None
#         self.vel_hist = deque(maxlen=5)
#         self.prev_sign = 0

#         self.vel_threshold = 0.0005
#         self.stop_threshold = 0.0002

#         self.stop_counter = 0
#         self.stop_points = int(0.2 * sample_rate)

#     # --- фильтр скорости ---
#     def _filtered_vel(self, v):
#         self.vel_hist.append(v)
#         return np.mean(self.vel_hist)

#     def _sign(self, v):
#         if abs(v) < self.vel_threshold:
#             return 0
#         return 1 if v > 0 else -1

#     # --- поиск минимума ---
#     def _detect_minimum(self, pos):

#         if self.prev_pos is None:
#             self.prev_pos = pos
#             return False

#         raw_v = pos - self.prev_pos
#         v = self._filtered_vel(raw_v)
#         sign = self._sign(v)

#         found = False

#         # ехали вниз → остановились или пошли вверх
#         if self.prev_sign == -1 and sign >= 0:
#             found = True

#         if sign != 0:
#             self.prev_sign = sign

#         self.prev_pos = pos

#         return found

#     # --- проверка полной остановки ---
#     def _detect_stop(self, pos):

#         if self.prev_pos is None:
#             self.prev_pos = pos
#             return False

#         v = abs(pos - self.prev_pos)

#         if v < self.stop_threshold:
#             self.stop_counter += 1
#         else:
#             self.stop_counter = 0

#         self.prev_pos = pos

#         return self.stop_counter > self.stop_points

#     # --- основной сценарий ---
#     def execute(self):

#         # 1️⃣ Медленно вниз
#         self.set_freq(self.freq_down)

#         while True:
#             pos = self.read_position()

#             if self._detect_minimum(pos):
#                 break

#             time.sleep(0.001)

#         # 2️⃣ Частота 0
#         self.set_freq(self.freq_zero)

#         # 3️⃣ Ждём выбег
#         time.sleep(0.3)

#         # 4️⃣ Проверяем остановку
#         while True:
#             pos = self.read_position()

#             if self._detect_stop(pos):
#                 break

#             time.sleep(0.001)

#         # 5️⃣ Чуть вверх (разгрузка механики)
#         self.set_freq(self.freq_up)
#         time.sleep(0.2)

#         # 6️⃣ Финальный стоп
#         self.set_freq(self.freq_zero)
