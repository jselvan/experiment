from dataclasses import dataclass
from typing import Tuple

from enum import Enum

from PIL.Image import Image

class ColourEnum(Enum):
    RED = '#ff0000'
    GREEN = '#00ff00'
    BLUE = '#0000ff'
    BLACK = '#000000'
    WHITE = '#ffffff'

class Colour:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b
    @classmethod
    def from_enum(cls, colour_enum: ColourEnum) -> 'Colour':
        return cls.from_hex(colour_enum.value)
    @classmethod
    def from_hex(cls, hex_str: str) -> 'Colour':
        hex_str = hex_str.lstrip('#')
        r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return cls(r, g, b)
    @classmethod
    def from_string(cls, colour_str: str) -> 'Colour':
        hex_str = ColourEnum[colour_str.upper()].value
        return cls.from_hex(hex_str)
    def to_hex(self) -> str:
        return '#{:02x}{:02x}{:02x}'.format(int(self.r * 255), int(self.g * 255), int(self.b * 255))
    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)
    def to_tuple_norm(self) -> Tuple[float, float, float]:
        return (self.r / 255.0, self.g / 255.0, self.b / 255.0)

class Primitive:
    pass

@dataclass
class GraphicPrimitive(Primitive):
    center: Tuple[float, float] # (x, y) coordinates
    def get_position(self) -> Tuple[float, float]:
        return self.center

@dataclass
class CirclePrimitive(GraphicPrimitive):
    center: Tuple[float, float]
    radius: float
    edgecolour: Colour | None
    facecolour: Colour | None
    linewidth: float

@dataclass
class RectanglePrimitive(GraphicPrimitive):
    center: Tuple[float, float]
    width: float
    height: float
    edgecolour: Colour | None
    facecolour: Colour | None
    linewidth: float
    orientation: float  # in degrees

@dataclass
class LinePrimitive(Primitive):
    start: Tuple[float, float]
    end: Tuple[float, float]
    colour: Colour
    linewidth: float

@dataclass
class ImagePrimitive(GraphicPrimitive):
    center: Tuple[float, float]
    width: float
    height: float
    imagedata: Image
    orientation: float  # in degrees
    
    @classmethod
    def from_path(cls, center: Tuple[float, float], width: float, height: float, image_path: str, orientation: float) -> 'ImagePrimitive':
        from PIL import Image as PILImage
        imagedata = PILImage.open(image_path)
        return cls(center=center, width=width, height=height, imagedata=imagedata, orientation=orientation)

