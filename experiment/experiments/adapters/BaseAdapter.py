import enum
from collections.abc import Sequence, Mapping

class BaseAdapter:
    def __init__(self, children: Sequence["BaseAdapter"]):
        self.active: bool = False
        self.children = children
        self.elapsed = 0.
        self.lifetimes = []

    def update(self, tick: float, events: Sequence["Event"]) -> bool:
        self.elapsed += tick
        # handle stop/pause events
        for child in self.children:
            child.update(tick, events)
        for child in self.children:
            if child.done:
                return False
        return True

    def render(self):
        for child in self.children:
            child.render()

    def reset(self):
        self.lifetimes.append(self.elapsed)
        self.elapsed = 0.
        self.active = False
        for child in self.children:
            child.reset()

