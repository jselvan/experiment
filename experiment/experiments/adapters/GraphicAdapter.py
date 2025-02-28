from pathlib import Path
from typing import Optional, Literal
from os import PathLike
from collections.abc import Sequence, Mapping

from numpy.typing import ArrayLike
import numpy as np
from PIL import Image

from experiment.renderers.base import Renderer
from experiment.experiments.adapters.BaseAdapter import BaseAdapter
from experiment.util.colours import parse_colour

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

TColour = Sequence[int] | str
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
        self.bbox = None if bbox is None else BBox.from_spec(bbox) 
    # update should be implemented for dynamic or animated stimuli
    def update(self, tick: float, events: Sequence["Event"]) -> bool:
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


class CircleAdapter(GraphicAdapter):
    def render(self, renderer: Renderer):
        renderer.draw_circle(self)

class RandomDotMotionAdapter(GraphicAdapter):
    def render(self, renderer: Renderer):
        renderer.draw_rdm(self)

cache = {}
cache_limit = 100

def load_and_cache_image(image: PathLike[bytes]) -> Image.Image:
    if image in cache:
        return cache[image]
    img = Image.open(image)
    if len(cache) > cache_limit:
        cache.popitem()
    cache[image] = img
    return img


class ImageAdapter(GraphicAdapter):
    def __init__(self, 
        image,
        position: Sequence[float], 
        size: Sequence[float],
        orientation: float=0,
        bbox: Optional[T_BBOX_SPEC]=None
    ):
        colour = 'WHITE'
        super().__init__(position, size, colour, orientation, bbox)
        if not isinstance(image, Image.Image):
            image_path = Path(image)
            image = load_and_cache_image(image_path)
        
        self.image: Image.Image = image
        print(self.image.mode, self.image.size)
        self.position = position
        self.size = size
        self.orientation = orientation
    @property
    def top_left(self):
        x, y = self.position
        w, h = self.size
        return int(x - w//2), int(y - h//2)
    def render(self, renderer: Renderer):
        renderer.draw_image(self)

class VideoAdapter(ImageAdapter):
    pass

class GaborAdapter(ImageAdapter):
    def __init__(self, 
        position: Sequence[int], 
        size: Sequence[int],
        lambda_: float,
        orientation: float,
        sigma: float,
        phase: float,
        trim: float=.005,
        bbox: Optional[T_BBOX_SPEC]=None,
        ):

        self.size = size
        self.lambda_ = lambda_
        self.orientation = orientation
        self.sigma = sigma
        self.phase = phase
        self.trim = trim
        image = self._compute()
        super().__init__(position=position, image=image, size=size, bbox=bbox)

    def _compute(self):
        w, h = self.size
        X0 = (np.linspace(1, w, w)/w)-.5
        Y0 = (np.linspace(1, h, h)/h)-.5
        Xm, Ym = np.meshgrid(X0, Y0)
        size = max(w, h)
        freq = size / self.lambda_
        phase = (self.phase/180)*np.pi

        theta = (self.orientation/180)*np.pi
        Xt = Xm * np.cos(theta)
        Yt = Ym * np.sin(theta)

        grating = np.sin(((Xt+Yt) * freq * 2 * np.pi) + phase)
        gauss = np.exp(-((Xm ** 2) + (Ym ** 2)) / (2 * (self.sigma / size)) ** 2)
        gauss[gauss < self.trim] = 0
        img_data = (grating * gauss + 1) / 2 * 255
        return Image.fromarray(img_data).convert('RGBA')

# class MovieAdapter(ImageAdapter, AudioAdapter):
#     pass
