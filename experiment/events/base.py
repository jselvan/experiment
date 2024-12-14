from collections.abc import Sequence
from experiment.events import Event

class EventManager:
    def post_event(self, event: Event):
        raise NotImplementedError()
    def get_events(self) -> Sequence[Event]:
        raise NotImplementedError()
