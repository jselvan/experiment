from __future__ import annotations
from typing import Tuple
from abc import ABC, abstractmethod


class BBox(ABC):
    """Abstract bounding-box for hit-testing.

    Implementations should provide `contains(center, pos)` which returns True
    when `pos` (x,y) is inside the bbox positioned at `center`.
    """

    @abstractmethod
    def contains(self, center: Tuple[float, float], pos: Tuple[float, float]) -> bool:
        ...

    @classmethod
    def from_dict(cls, data):
        """Factory: accept a dict or BBox and return a BBox instance or None."""
        if data is None:
            return None
        if isinstance(data, BBox):
            return data
        if not isinstance(data, dict):
            raise ValueError('BBox.from_dict expects a dict or BBox instance')
        t = data.get('type')
        if t == 'circle' or 'radius' in data:
            radius = data.get('radius')
            if radius is None:
                raise ValueError('circle bbox requires radius')
            return CircleBBox(radius)
        if t == 'rect' or ('width' in data and 'height' in data):
            return RectBBox(data['width'], data['height'])
        raise ValueError('Unknown bbox dict format')


class CircleBBox(BBox):
    def __init__(self, radius: float):
        self.radius = float(radius)

    def contains(self, center: Tuple[float, float], pos: Tuple[float, float]) -> bool:
        dx = pos[0] - center[0]
        dy = pos[1] - center[1]
        return (dx * dx + dy * dy) <= (self.radius * self.radius)


class RectBBox(BBox):
    def __init__(self, width: float, height: float):
        self.width = float(width)
        self.height = float(height)

    def contains(self, center: Tuple[float, float], pos: Tuple[float, float]) -> bool:
        halfw = self.width / 2.0
        halfh = self.height / 2.0
        return (center[0] - halfw) <= pos[0] <= (center[0] + halfw) and (center[1] - halfh) <= pos[1] <= (center[1] + halfh)

    @classmethod
    def from_dict(cls, data):
        # not used directly, factory handled on base class
        return cls(data.get('width'), data.get('height'))


# legacy helper removed; use BBox.from_dict classmethod
