from typing import Sequence, Optional

from experiment.task.adapters.graphic.base import GraphicAdapter
from experiment.components.renderer.base import Renderer
from experiment.util.colours import TColour
from experiment.util.bbox import T_BBOX_SPEC

class RectAdapter(GraphicAdapter):
    def __init__(self, 
        position: Sequence[float], 
        size: Sequence[float] | float, 
        colour: TColour,
        orientation: float=0,
        bbox: Optional[T_BBOX_SPEC]=None
        ):
        super().__init__(position, size, colour, orientation, bbox)
        cx, cy = self.position
        if not isinstance(self.size, Sequence):
            raise TypeError("For Rect, size must be tuple of 2")
        sx, sy = self.size
        x = int(cx - sx//2)
        y = int(cy - sy//2)
        self.rect = x, y, sx, sy
    def render(self, renderer: Renderer):
        renderer.draw_rect(self)
