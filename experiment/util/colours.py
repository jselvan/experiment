from typing import Sequence

named_colours = {
    'BLACK': [0,0,0],
    'WHITE': [255,255,255],
    'RED': [255,0,0],
    'GREEN': [0,255,0],
    'BLUE': [0,0,255],
    'YELLOW': [255,255,0],
    'CYAN': [0,255,255],
    'MAGENTA': [255,0,255],
    'GRAY': [128,128,128],
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
