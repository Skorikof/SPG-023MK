class CollectorService:
    def __init__(self, model):
        self.model = model
        self.flag_collect_done = False

    def set_done(self, flag: bool):
        self.flag_collect_done = flag

    def consume_done(self) -> bool:
        if self.flag_collect_done:
            self.flag_collect_done = False
            return True
        return False

    def start(self, with_data: bool):
        self.flag_collect_done = False
        if with_data:
            self.model.run_collector_with_data()
        else:
            self.model.run_collector_without_data()
        self.model.reader_start_test()

    def start_find_stroke(self):
        self.flag_collect_done = False
        self.model.run_collector_find_stroke()
        self.model.reader_start_test()

    def stop(self):
        self.model.reader_stop_test()
        self.model.write_bit_force_cycle(0)
