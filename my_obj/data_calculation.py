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
    def calc_middle_min_and_max_force(self, data: list):
        try:
            comp_index = data.index(max(data))
            comp_list = [abs(x) for x in data[comp_index - 10:comp_index + 10]]
            max_comp = sum(comp_list) / len(comp_list)

            recoil_index = data.index(min(data))
            recoil_list = [abs(x) for x in data[recoil_index - 10:recoil_index + 10]]
            max_recoil = sum(recoil_list) / len(recoil_list)

            return max_recoil, max_comp

        except Exception as e:
            print(f'ERROR in data_calculation/calc_middle_min_and_max_force - {e}')

    def calc_offset_move_by_hod(self, obj, min_p):
        try:
            return round((obj.max_length - obj.min_length - obj.hod) / 2 + min_p, 2)

        except Exception as e:
            print(f'ERROR in data_calculation/calc_offset_move - {e}')

    def calc_power(self, move: list, force: list):
        try:
            temp = 0
            for i in range(1, len(move)):
                temp = round(temp + abs(move[i] - abs(move[i - 1])) * abs(force[i - 1]), 1)

            temp = round((temp * 0.009807) / 1000, 1)

            return temp

        except Exception as e:
            print(f'ERROR in data_calculation/calc_power - {e}')

    def calc_freq_piston(self, speed, hod):
        try:
            return round(speed / (hod * 0.002 * 3.14), 3)

        except Exception as e:
            print(f'ERROR in data_calculation/calc_freq_piston - {e}')
