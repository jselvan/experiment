from typing import Sequence, Optional
from experiment.components.events import Event
from experiment.components.renderer.base import Renderer

class BaseAdapter:
    def __init__(self, children: Optional[Sequence["BaseAdapter"]] = None):
        self.active: bool = False
        if children is None:
            children = []
        self.children = children
        self.elapsed = 0.
        self.lifetimes = []

    def start(self):
        self.active = True 
        for child in self.children:
            child.start()

    def update(self, tick: float, events: Sequence["Event"]) -> bool:
        self.elapsed += tick
        # handle stop/pause events
        for child in self.children:
            child.update(tick, events)
        for child in self.children:
            if not child.active:
                return False
        return True

    def render(self, renderer: "Renderer"):
        for child in self.children:
            child.render(renderer)

    def reset(self):
        self.lifetimes.append(self.elapsed)
        self.elapsed = 0.
        self.active = False
        for child in self.children:
            child.reset()

