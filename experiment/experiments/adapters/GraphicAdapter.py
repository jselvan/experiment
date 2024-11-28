from collections.abc import Sequence

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


class GraphicAdapter(BaseAdapter):
    def __init__(self, position: Sequence[float], size: Sequence[float] | float, colour: Sequence[int] | str):
        super().__init__()
        self.position = position
        self.size = size
        self.colour = parse_colour(colour)
    # update should be implemented for dynamic or animated stimuli
    def render(self, renderer: Renderer):
        raise NotImplementedError

class RectAdapter(GraphicAdapter):
    def render(self, renderer: Renderer):
        renderer.draw_rect(self)

class CircleAdapter(GraphicAdapter):
    def render(self, renderer: Renderer):
        renderer.draw_circle(self)

