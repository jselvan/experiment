from typing import List
from experiment.components.events import Event
from experiment.components import BaseComponent

class EventManager(BaseComponent):
    COMPONENT_TYPE = "event_manager"
    def __init__(self):
        super().__init__()
        self.event_queue = []
        self.message_handlers = {
            "event": self.parse_event_message
        }
    def post_event(self, event: Event):
        if not self.manager:
            raise RuntimeError("EventManager must be registered with a Manager before posting events.")
        if event.data.get('time') is None:
            event.data['time'] = self.manager.get_time()
        self.event_queue.append(event)
    def get_events(self) -> List[Event]:
        events = self.event_queue.copy()
        self.event_queue.clear()
        return events
    def parse_event_message(self, message, announcer):
        self.post_event(message)