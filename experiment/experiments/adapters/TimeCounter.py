from collections.abc import Sequence
from experiment.experiments.events import Event
from experiment.experiments.adapters.BaseAdapter import BaseAdapter

class TimeCounter(BaseAdapter):
    def __init__(self, children: Sequence[BaseAdapter], duration: float):
        super().__init__(children)
        #TODO: add on complete callback?
        self.duration = duration

    def update(self, tick: float, events: Sequence[Event]) -> None:
        super().update(tick, events)
        if self.active and self.duration is not None:
            self.elapsed += tick
            if self.duration <= self.elapsed:
                self.active = False
