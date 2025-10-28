from typing import Sequence
from experiment.experiments.adapters import BaseAdapter, TimeCounter
from experiment.events import Event

class ButtonAdapter(BaseAdapter):
    def __init__(self,
        time_counter: TimeCounter | float | int | None,
        keys: Sequence[str],
        children: Sequence[BaseAdapter] | None = None,
    ):
        self.time_counter = TimeCounter.new(time_counter)
        children = children + [self.time_counter] if children is not None else [self.time_counter]
        super().__init__(children=children)
        self.keys = keys

        self.pressed = None
        self.state = 'init'
    
    def update(self, tick: float, events: Sequence["Event"]) -> bool:
        super().update(tick, events)
        if not self.time_counter.active:
            self.state = 'elapsed'
            self.active = False
            return self.active
        
        key_event = any(event['type']=='key_down' for event in events) 
        if not key_event:
            return self.active

        for event in events:
            if event['type'] == 'key_down' and event['key'] in self.keys:
                # log the touch
                # if event codes are provided, fire one off now
                # we have made a "correct" touch
                # we will stop
                self.state = 'correct'
                self.pressed = event['key']
                self.active = False
                break

        return self.active