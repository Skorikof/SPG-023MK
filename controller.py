import os


class Controller:
    def __init__(self, model):
        try:
            self.model = model

            self.model.start_param()

            self.values_time = []
            self.values_f = []
            self.values_move = []
            self.values_state = []
            self.time_proc = []

            self.check_directory()
            self.init_signals()

        except Exception as e:
            self.model.save_log('error', str(e))

    def check_directory(self):
        current_dir = os.getcwd()
        os.chdir(current_dir)
        if not os.path.exists('archive'):
            os.mkdir('archive')
        elif not os.path.exists('log'):
            os.mkdir('log')

    def init_signals(self):
        self.model.signals.read_result_buffer.connect(self.result_test)

    # def move_detection(self):
    #     try:
    #         self.model.remember_start_pos()
    #         self.model.set_regs['force_alarm'] = 2000
    #         self.model.write_emergency_force()
    #
    #         self.model.set_regs['frequency'] = int(10) * 100
    #         self.model.write_frequency()
    #
    #         self.model.set_regs['adr_freq'] = 1
    #         self.model.motor_up()
    #
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in controller/move_detection - {}'.format(e)
    #         self.model.status_bar_msg(txt_log)
    #         self.model.save_log('error', str(e))

    def result_test(self, result):
        try:
            self.values_time = result.get('count')
            self.values_f = result.get('force')
            self.values_move = result.get('move')
            self.values_state = result.get('state')
            self.time_proc = result.get('time')

            self.save_result_test()

        except Exception as e:
            txt_log = 'ERROR in controller/result_test - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

    def save_result_test(self):
        try:
            with open('testData.dat', 'w') as file_dat:
                for i in range(0, len(self.values_f)):
                    str_f = str(i) + ' Время: ' + str(self.values_time[i]) + \
                        ' Статус: ' + str(self.values_state[i]) + \
                        ' F = ' + str(self.values_f[i]) + \
                        ' H = ' + str(self.values_move[i]) + '\n'
                    file_dat.write(str_f)

                file_dat.write('=' * 50 + '\n')

        except Exception as e:
            txt_log = 'ERROR in controller/save_result_test - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

