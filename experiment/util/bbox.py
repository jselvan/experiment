from typing import Mapping, Literal

T_BBOX_SPEC = Mapping[Literal['width','height'], float]

class BBox:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    @classmethod
    def from_spec(cls, spec: T_BBOX_SPEC):
        return cls(**spec)
    def detect_touch(self, adapter, events):
        cx, cy = adapter.position
        hw, hh = self.width/2, self.height/2
        xmin, xmax = cx - hw, cx + hw
        ymin, ymax = cy - hh, cy + hh
        for event in events:
            ex, ey = event.get('x'), event.get('y')
            if ex is None or ey is None:
                continue
            if (xmin<ex<xmax) and (ymin<ey<ymax):
                return True
        return False