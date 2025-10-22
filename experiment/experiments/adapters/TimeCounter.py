from typing import Sequence, Optional
from experiment.events import Event
from experiment.experiments.adapters.BaseAdapter import BaseAdapter

class TimeCounter(BaseAdapter):
    def __init__(self, 
            duration: float | int | None, 
            children: Optional[Sequence[BaseAdapter]]=None,
            on_enter: Optional[callable]=None,
            on_exit: Optional[callable]=None
        ):
        super().__init__(children)
        self.duration = duration
        self.on_enter = on_enter
        self.on_exit = on_exit
        if duration is None and on_exit is not None:
            raise ValueError("on_exit callback requires a defined duration")

    def start(self) -> None:
        super().start()
        if self.on_enter is not None:
            self.on_enter(self)

    def update(self, tick: float, events: Sequence[Event]) -> bool:
        super().update(tick, events)
        if self.active and self.duration is not None and self.duration <= self.elapsed:
            self.active = False
            if self.on_exit is not None:
                self.on_exit(self)
        return self.active

    @classmethod
    def new(cls, timecounter: "TimeCounter | float | int | None") -> "TimeCounter":
        if isinstance(timecounter, TimeCounter):
            return timecounter
        return cls(timecounter)