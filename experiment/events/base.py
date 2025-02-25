from collections.abc import Sequence
from experiment.events import Event

class EventManager:
    def __init__(self, manager: "Manager"):
        self.manager = manager
    def post_event(self, event: Event):
        raise NotImplementedError()
    def get_events(self) -> Sequence[Event]:
        raise NotImplementedError()
