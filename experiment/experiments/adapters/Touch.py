from collections.abc import Sequence, Mapping
from experiment.experiments.adapters.BaseAdapter import BaseAdapter
from experiment.experiments.adapters.GraphicAdapter import GraphicAdapter
from experiment.experiments.adapters.TimeCounter import TimeCounter
from experiment.experiments.events import Event

class TouchAdapter(BaseAdapter):
    def __init__(self, 
        time_counter: TimeCounter, 
        items: Mapping[str, GraphicAdapter], 
        targets: Sequence[str] | None = None, 
        event_code_map: Mapping[str, int] | None = None,
        allow_outside_touch: bool = False, 
        allow_non_target_touch: bool = False
    ):
        self.time_counter = time_counter
        self.items = items
        self.targets = targets
        self.allow_non_target_touch = allow_non_target_touch
        self.allow_outside_touch = allow_outside_touch
        self.event_code_map = event_code_map
        self.state = 'init'
    def update(self, tick: float, events: Sequence["Event"]) -> None:
        # update timer, and if expired, stop analyzing
        self.time_counter.update(tick, events)
        if self.time_counter.done:
            self.state = 'elapsed'
            return

        # update all stimuli
        for item in self.items.values():
            item.update(tick, events)
        
        # check if item was touched
        for name, item in self.items.items():
            if item.was_touched:
                # log the touch
                # if event codes are provided, fire one off now
                if self.targets is None or name in self.targets:
                    # we have made a "correct" touch
                    # we will stop
                    pass
                elif self.allow_non_target_touch:
                    # we have made an incorrect touch
                    # but this is allowed, continue 
                    pass
                else:
                    # we have made an incorrect touch
                    # and this is not permitted, we will stop
                    pass
        # if any events are unconsumed, check if they fell outside. 
        # if so, and allow_outside_touch is false, end otherwise continue

    def render(self):
        # draw all the items on screen
        for item in self.items.values():
            item.render()
## CHATGPT suggestion
# def update(self, tick: float, events: Sequence[Event]) -> None:
#     # Update timer
#     self.time_counter.update(tick, events)
#     if self.time_counter.done:
#         self.state = 'elapsed'
#         return

#     # Update items
#     for name, item in self.items.items():
#         item.update(tick, events)

#         if item.was_touched:
#             self.handle_touch(name)

#     # Handle external touches
#     if not self.allow_outside_touch:
#         for event in events:
#             if self.is_outside_touch(event):
#                 self.state = 'outside_touch'
#                 return

# def handle_touch(self, name: str):
#     if self.targets is None or name in self.targets:
#         print(f"Correct touch: {name}")
#         self.state = 'correct'
#     elif self.allow_non_target_touch:
#         print(f"Incorrect touch (allowed): {name}")
#         self.state = 'incorrect_allowed'
#     else:
#         print(f"Incorrect touch (not allowed): {name}")
#         self.state = 'incorrect'
