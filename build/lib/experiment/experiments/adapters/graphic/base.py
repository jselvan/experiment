from typing import Optional, Sequence
from experiment.experiments.adapters.BaseAdapter import BaseAdapter
from experiment.renderers.base import Renderer
from experiment.events import Event
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
        if isinstance(self.size, (int, float)):
            self.bbox = BBox(self.size, self.size)
        else:
            assert len(self.size) == 2, "Size must be a sequence of two dimensions for CircleAdapter"
            self.bbox = BBox(self.size[0], self.size[1])
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