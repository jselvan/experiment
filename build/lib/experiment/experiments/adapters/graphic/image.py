from typing import Optional, Sequence
from os import PathLike
from pathlib import Path

from PIL import Image

from experiment.util.bbox import T_BBOX_SPEC
from experiment.util.colours import parse_colour

from experiment.experiments.adapters.graphic.base import GraphicAdapter
from experiment.renderers.base import Renderer

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
    @classmethod
    def new(cls,
        position: Sequence[float],
        size: Sequence[float],
        resolution: Sequence[int],
        orientation: float=0,
        bbox: Optional[T_BBOX_SPEC]=None,
        colour: str='WHITE',
    ):
        colour = tuple(parse_colour(colour))
        image = Image.new(
            'RGB', 
            resolution, 
            colour
        )
        return cls(
            image=image,
            position=position,
            size=size,
            orientation=orientation,
            bbox=bbox
        )