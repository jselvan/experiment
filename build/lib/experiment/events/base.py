from collections.abc import Sequence
from experiment.events import Event

class EventManager:
    def __init__(self, manager: "Manager"):
        self.manager = manager
        self.event_queue = []
    def post_event(self, event: Event):
        if event.get('time') is None:
            event['time'] = self.manager.get_time()
        self.event_queue.append(event)
    def get_events(self) -> Sequence[Event]:
        events = self.event_queue.copy()
        self.event_queue.clear()
        return events
