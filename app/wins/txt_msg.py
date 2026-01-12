class TextMsg:
    def msg_from_controller(msg):
        msg_dict = {'welcome': ('info',
                                f'Здравствуйте\nДобро пожаловать\nв\nпрограмму.\n'\
                                f'Выберите необходимый\nпункт меню'),
                    'connect_lost': ('attention',
                                     'ОТСУТСТВУЕТ\nПОДКЛЮЧЕНИЕ\nК\nКОНТРОЛЛЕРУ'),
                    'red_btn': ('warning',
                                'РАБОТА ПРЕРВАНА\nПО КОМАНДЕ\nОПЕРАТОРА'),
                    'traverse_referent': ('attention',
                                          'ОПРЕДЕЛЕНИЕ\nРЕФЕРЕНТНОЙ ТОЧКИ\nТРАВЕРСЫ'),
                    'pos_traverse': ('attention',
                                     'ПОЗИЦИОНИРОВАНИЕ\nТРАВЕРСЫ'),
                    'yellow_btn': ('question',
                                   'НАЖМИТЕ\nЖЁЛТУЮ\nКНОПКУ\nДЛЯ ЗАПУСКА\nИСПЫТАНИЯ'),
                    'move_detection': ('attention',
                                       'ВНИМАНИЕ!\nБудет произведено\nопределение хода'),
                    'gear_set_pos': ('attention',
                                     f'ВНИМАНИЕ!\nПРОВОРОТ ПРИВОДА\n'\
                                     f'В ПОЛОЖЕНИЕ\nДЛЯ РЕГУЛИРОВКИ ХОДА'),
                    'pumping': ('attention',
                                'ПРОКАЧКА\nАМОРТИЗАТОРА'),
                    'lost_control': ('warning',
                                     'ПОТЕРЯНО\nУПРАВЛЕНИЕ'),
                    'excess_force': ('warning',
                                     'ПРЕВЫШЕНИЕ\nУСИЛИЯ'),
                    'excess_temperature': ('warning',
                                           'ПРЕВЫШЕНА\nМАКСИМАЛЬНО\nДОПУСТИМАЯ\nТЕМПЕРАТУРА'),
                    'safety_fence': ('warning',
                                     'ОТКРЫТО\nЗАЩИТНОЕ\nОГРАЖДЕНИЕ'),
                    'alarm_traverse_up': ('warning',
                                          f'ТРАВЕРСА\nВ ВЕРХНЕМ\nПОЛОЖЕНИИ!\nНАЖМИТЕ\n'\
                                          f'КНОПКУ РАЗБЛОКИРОВКИ\nИ УДЕРЖИВАЯ ЕЁ\n'\
                                          f'НАЖМИТЕ КНОПКУ\nНА ЭКРАНЕ'),
                    'alarm_traverse_down': ('warning',
                                            f'ТРАВЕРСА\nВ НИЖНЕМ\nПОЛОЖЕНИИ!\nНАЖМИТЕ\n'\
                                            f'КНОПКУ РАЗБЛОКИРОВКИ\nИ УДЕРЖИВАЯ ЕЁ\n'\
                                            f'НАЖМИТЕ КНОПКУ\nНА ЭКРАНЕ'),
                    'traverse_block': ('warning',
                                       'ТРАВЕРСА\nНЕ РАЗБЛОКИРОВАНА'),
                    'traverse_unblock': ('warning',
                                         'ТРАВЕРСА\nНЕ ЗАБЛОКИРОВАНА')
                    }      

        find_msg = msg_dict.get(msg, (None, None))
        tag, txt = find_msg[0], find_msg[1]

        return tag, txt
