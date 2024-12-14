from typing import Optional, Literal
from collections.abc import Sequence, Mapping

from experiment.renderers.base import Renderer
from experiment.experiments.adapters.BaseAdapter import BaseAdapter

named_colours = {
    'BLACK': [0,0,0],
    'WHITE': [255,255,255]
}

def parse_colour_hex(colour: str):
    colour = colour.strip('#')
    if not len(colour)==6:
        raise ValueError("Provided colour hex is invalid: #{colour}")
    rgb = colour[:2], colour[2:4], colour[4:]
    return [int(value, base=16) for value in rgb]

def parse_colour(colour: str | Sequence[int]):
    if isinstance(colour, str):
        if colour.startswith('#'):
            return parse_colour_hex(colour)
        elif colour in named_colours:
            return named_colours[colour]
        else:
            raise ValueError(f"Provided colour is an invalid string: {colour}")
    else:
        # colour must be a sequence otherwise, 
        # ensure values are between 0 and 255
        # and are integers
        if all((isinstance(value, int) and 0 <= value <= 255) for value in colour):
            return colour
        else:
            raise ValueError(f"Provided colour is an invalid sequence: {colour}")

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


class ImageAdapter(GraphicAdapter):
    def __init__(self, position, image):
        pass 

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
        trim: float=.005):

        self.size = size
        self.lambda_ = lambda_
        self.orientation = orientation
        self.sigma = sigma
        self.phase = phase
        self.trim = trim
        image = self._compute()
        super().__init__(position=position, image=image)

    def _compute(self):
        import numpy as np
        from PIL import Image
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
        return Image.fromarray(img_data)

# class MovieAdapter(ImageAdapter, AudioAdapter):
#     pass
