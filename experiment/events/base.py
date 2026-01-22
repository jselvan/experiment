from abc import ABC, abstractmethod
from experiment.components import BaseComponent
from experiment.events.bus import EventBus

class EventSource(BaseComponent, ABC):
    def __init__(self):
        super().__init__()
        self.bus: EventBus | None = None
    def set_bus(self, bus: EventBus):
        self.bus = bus
    @abstractmethod
    def poll(self):
        """Retrieve events from the source."""
        ...