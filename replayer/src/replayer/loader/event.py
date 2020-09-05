class Event:
    def __init__(self, pid, event_type, event_data):
        self.pid = pid
        self.event_type = event_type
        self.event_data = event_data
    
    def __repr__(self):
        return f"<PID {self.pid} : {self.event_data} >"

