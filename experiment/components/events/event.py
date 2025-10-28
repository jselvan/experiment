from typing import Optional, Dict

class Event:
    def __init__(self, type=None, data: Optional[Dict]=None):
        self.type = type
        self.data = data if data is not None else {}

    @classmethod
    def from_message(cls, message, announcer):
        # Parse the message and create an Event instance
        return cls()

class TouchEvent(Event):
    def __init__(self):
        pass

class SystemEvent(Event):
    def __init__(self):
        pass