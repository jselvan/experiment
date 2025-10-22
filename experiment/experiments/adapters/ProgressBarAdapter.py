
from experiment.experiments.adapters.graphic.rect import RectAdapter

from typing import Sequence
from experiment.events import Event

class ProgressBarAdapter(RectAdapter):
    def __init__(self, **kwargs):
        self.duration = kwargs.pop('duration')
        super().__init__(**kwargs)
        self.original_size = self.size

    def start(self):
        super().start()

    def update(self, tick: float, events: Sequence["Event"]) -> bool:
        self.active = super().update(tick, events)
        progress = min(self.elapsed / self.duration, 1.0)
        if progress >= 1.0:
            self.active = False
            return False

        self.size = (self.original_size[0] * (1 - progress), self.original_size[1])
        self.rect = (
            self.position[0],
            self.position[1],
            self.size[0],
            self.size[1],
        )
        return True

    def reset(self):
        super().reset()
        self.size = self.original_size
