from typing import Callable
from collections.abc import Sequence

from experiment.experiments.adapters.BaseAdapter import BaseAdapter
from experiment.renderers.base import Renderer

class BaseAnimationAdapter(BaseAdapter):
    """ Base Class for Animation Adapters

    Parameters
    ----------
    child: BaseAdapter
        Animated properties are propogated down to child adapters
    duration: float
        Duration in seconds of the whole animation
    timing_function: Callable[float, float] | str | None
        Allows modifying the animation curve. By default None, linear
        If callable, accepts a value between 0 and 1 and return a value between 0 and 1
    """
    def __init__(self, 
                 child: BaseAdapter, 
                 duration: float, 
                 timing_function: Callable[[float], float] | str | None=None):
        super().__init__()
        self.child = child
        self.duration = duration
        self.elapsed = 0.
        if isinstance(timing_function, str):
            raise NotImplementedError("Timing function lookup not implemented")
        self.timing_function = timing_function
        
    def update(self, tick: float, events: Sequence["Event"]):
        # Update self and propagate updates down the chain
        super().update(tick, events)
        self.animate(self.get_progress())
        self.child.update(tick, events)

    def animate(self, progress: float):
        raise NotImplementedError()

    def get_progress(self):
        progress = min(self.elapsed / self.duration, 1.)
        if self.timing_function is not None:
            progress = self.timing_function(progress)
        return progress

    def render(self, renderer: Renderer):
        self.child.render(renderer)
