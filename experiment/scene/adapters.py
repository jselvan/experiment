from typing import Iterable, List, Tuple
from experiment.rendering.primitives import Primitive, CirclePrimitive, RectanglePrimitive, Colour
from experiment.scene.bbox import BBox, CircleBBox, RectBBox
import math


class StaticGraphicAdapter:
    """Adapter that returns a fixed list of primitives each frame.

    Accepts an optional `bbox` dict for touch detection. Supported formats:
      - {'radius': r} for circular hitbox
      - {'width': w, 'height': h} for rectangular hitbox

    Subclasses may override `contains_point` to provide custom behaviour.
    """

    def __init__(self, primitives: Iterable[Primitive], bbox: BBox | dict | None = None):
        self.primitives = list(primitives)
        # support legacy dict bboxes by converting into BBox instances
        if isinstance(bbox, dict):
            bbox = BBox.from_dict(bbox)
        self.bbox = bbox

    def get_primitives(self):
        return list(self.primitives)

    def contains_point(self, pos: Tuple[float, float]) -> bool:
        # if subclass provides bbox-aware detection, respect it first
        if self.bbox:
            center = None
            if self.primitives:
                p = self.primitives[0]
                if hasattr(p, 'center'):
                    center = p.center
            if center is None:
                return False
            # self.bbox is a BBox instance; use its contains method
            return self.bbox.contains(center, pos)
        return False


class CircleAdapter(StaticGraphicAdapter):
    def __init__(self, center=(320, 240), radius=40, edgecolour=Colour(255,255,255), facecolour=Colour(255,0,0), linewidth=2, bbox: BBox | dict | None = None):
        self.center = tuple(float(c) for c in center)
        self.radius = float(radius)
        prim = CirclePrimitive(center=self.center, radius=self.radius, edgecolour=edgecolour, facecolour=facecolour, linewidth=linewidth)
        # by default set bbox to the circle radius if not provided
        if bbox is None:
            bbox = CircleBBox(self.radius)
        super().__init__([prim], bbox=bbox)

    def contains_point(self, pos: Tuple[float, float]) -> bool:
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return (dx*dx + dy*dy) <= (self.radius * self.radius)


class RectAdapter(StaticGraphicAdapter):
    def __init__(self, center=(420, 240), width=80, height=80, edgecolour=Colour(0,0,0), facecolour=Colour(0,0,255), linewidth=2, orientation=0, bbox: BBox | dict | None = None):
        self.center = tuple(float(c) for c in center)
        self.width = float(width)
        self.height = float(height)
        prim = RectanglePrimitive(center=self.center, width=self.width, height=self.height, edgecolour=edgecolour, facecolour=facecolour, linewidth=linewidth, orientation=orientation)
        if bbox is None:
            bbox = RectBBox(self.width, self.height)
        super().__init__([prim], bbox=bbox)

    def contains_point(self, pos: Tuple[float, float]) -> bool:
        halfw = self.width / 2.0
        halfh = self.height / 2.0
        return (self.center[0] - halfw) <= pos[0] <= (self.center[0] + halfw) and (self.center[1] - halfh) <= pos[1] <= (self.center[1] + halfh)

