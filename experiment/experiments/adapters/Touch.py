from collections.abc import Sequence, Mapping
from experiment.experiments.adapters.BaseAdapter import BaseAdapter
from experiment.experiments.adapters.GraphicAdapter import GraphicAdapter
from experiment.experiments.adapters.TimeCounter import TimeCounter
from experiment.events import Event

class TouchAdapter(BaseAdapter):
    def __init__(self, 
        time_counter: TimeCounter, 
        items: Mapping[str, GraphicAdapter], 
        targets: Sequence[str] | None = None, 
        event_code_map: Mapping[str, int] | None = None,
        allow_outside_touch: bool = False, 
        allow_non_target_touch: bool = False
    ):
        children = [time_counter] + list(items.values())
        super().__init__(children=children)
        self.time_counter = time_counter
        self.items = items
        self.targets = targets
        self.allow_non_target_touch = allow_non_target_touch
        self.allow_outside_touch = allow_outside_touch
        self.event_code_map = event_code_map
        self.state = 'init'

    def update(self, tick: float, events: Sequence["Event"]) -> bool:
        super().update(tick, events)
        if not self.time_counter.active:
            self.state = 'elapsed'
            self.active = False
            return self.active
        
        touch_event = any(event['type']=='mouse_down' for event in events) 
        if not touch_event:
            return self.active
        touch_outside = True # guilty until proven innocent
        for name, item in self.items.items():
            if item.was_touched:
                # log the touch
                # if event codes are provided, fire one off now
                if self.targets is None or name in self.targets:
                    # we have made a "correct" touch
                    # we will stop
                    self.state = 'correct'
                    self.chosen = name
                    self.active = False
                    touch_outside = False
                    break
                elif self.allow_non_target_touch:
                    # we have made an incorrect touch
                    # but this is allowed, continue 
                    touch_outside = False
                else:
                    # we have made an incorrect touch
                    # and this is not permitted, we will stop
                    self.state = 'incorrect'
                    self.chosen = name
                    self.active = False
                    touch_outside = False
                    break
        # if any events are unconsumed, the touch fell out
        if touch_outside and not self.allow_outside_touch:
            # if so, and allow_outside_touch is false, end otherwise continuepass
            self.state = 'outside'
            self.active = False
        return self.active
