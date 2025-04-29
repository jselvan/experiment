from typing import Sequence, Optional
from experiment.events import Event
from experiment.experiments.adapters.BaseAdapter import BaseAdapter

class TimeCounter(BaseAdapter):
    def __init__(self, 
            duration: float | int | None, 
            children: Optional[Sequence[BaseAdapter]]=None):
        super().__init__(children)
        self.duration = duration

    def update(self, tick: float, events: Sequence[Event]) -> None:
        super().update(tick, events)
        if self.active:
            self.elapsed += tick
            if self.duration is not None and self.duration <= self.elapsed:
                self.active = False
    
    @classmethod
    def new(cls, timecounter: "TimeCounter | float | int | None") -> "TimeCounter":
        if isinstance(timecounter, TimeCounter):
            return timecounter
        return cls(timecounter)