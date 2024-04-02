class Controller:
    def __init__(self, model):
        try:
            self.model = model

            self.model.start_param()

        except Exception as e:
            self.model.save_log('error', str(e))
