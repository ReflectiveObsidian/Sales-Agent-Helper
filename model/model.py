class Model:
    def __init__(self, view):
        self.view = view
        self.call_logs_observers = []

        self.call_logs = []
        self.emotion = [""]
        self.personalities = [""]
        self.warnings = [""]

    def set_call_log_observer(self, observer):
        self.call_logs_observers.append(observer)

    def update_call_log_observers(self):
        for observer in self.call_logs_observers:
            observer(self.call_logs)

    def get_call_logs(self):
        return self.call_logs
    
    def add_call_log(self, call_log):
        self.call_logs.append(call_log)
        self.update_call_log_observers()
        self.__update_view()

    def clear_call_logs(self):
        self.call_logs = []
        self.update_call_log_observers()
        self.__update_view()

    def get_emotion(self):
        return self.emotion
    
    def set_emotion(self, emotion):
        self.emotion = emotion
        self.__update_view()

    def get_personalities(self):
        return self.personalities
    
    def set_personalities(self, personalities):
        self.personalities = personalities
        self.__update_view()

    def get_warnings(self):
        return self.warnings
    
    def set_warnings(self, warnings):
        self.warnings = warnings
        self.__update_view()

    def __update_view(self):
        self.view.update(self)
        