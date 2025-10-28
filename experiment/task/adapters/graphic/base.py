from typing import Optional, Sequence
from experiment.task.adapters.BaseAdapter import BaseAdapter
from experiment.components.renderer.base import Renderer
from experiment.components.events import Event
from experiment.util.colours import parse_colour, TColour
from experiment.util.bbox import BBox, T_BBOX_SPEC

class GraphicAdapter(BaseAdapter):
    def __init__(self, 
        position: Sequence[float], 
        size: Sequence[float] | float, 
        colour: TColour, 
        orientation: float=0,
        bbox: Optional[T_BBOX_SPEC]=None):

        super().__init__(children=[])
        self.position = position
        self.size = size
        self.colour = parse_colour(colour)
        self.orientation = orientation
        self.was_touched = False
        if bbox is None:
            self.infer_bbox()
        else:
            self.bbox = BBox.from_spec(bbox)
    def infer_bbox(self):
        if isinstance(self.size, Sequence):
            self.bbox = BBox(self.size[0], self.size[1])
        else:
            self.bbox = BBox(self.size, self.size)
    # update should be implemented for dynamic or animated stimuli
    def update(self, tick: float, events: Sequence[Event]) -> bool:
        super().update(tick, events)
        if self.bbox is not None:
            if self.bbox.detect_touch(self, events):
                self.was_touched = True 
            else:
                self.was_touched = False
        return True
    def reset(self):
        super().reset()
        self.was_touched = False
    def render(self, renderer: Renderer):
        raise NotImplementedError()