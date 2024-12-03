class SpeedLimitForHod:
    def calculate_speed_limit(self, hod):
        if 40 <= hod < 50:
            return 0.41
        elif 50 <= hod < 60:
            return 0.51
        elif 60 <= hod < 70:
            return 0.62
        elif 70 <= hod < 80:
            return 0.72
        elif 80 <= hod < 90:
            return 0.82
        elif 90 <= hod < 100:
            return 0.92
        elif 100 <= hod < 110:
            return 1.03
        elif 110 <= hod < 120:
            return 1.13
        elif hod == 120:
            return 1.23
        else:
            return 0.41


class CalcData:
    def calc_power(self, move: list, force: list):
        try:
            temp = 0
            for i in range(1, len(move)):
                temp = round(temp + abs(move[i] - abs(move[i - 1])) * abs(force[i - 1]), 1)

            temp = round((temp * 0.009807) / 1000, 1)

            return temp

        except Exception as e:
            print(f'ERROR in model/_calc_power - {e}')

    def calc_freq_piston(self, speed, hod):
        try:
            return round(speed / (hod * 0.002 * 3.14), 3)

        except Exception as e:
            print(f'ERROR in model/_calc_freq_piston - {e}')

