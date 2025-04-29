import pygame
from typing import Optional, Sequence
from experiment.renderers.base import Renderer
from experiment.experiments.adapters.graphic import *
from experiment.util.colours import parse_colour

class PygameRenderer(Renderer):
    def __init__(self, display_params, background=None):
        self.display_params = display_params
        fullscreen = self.display_params.pop('fullscreen', False)
        if fullscreen:
            self.display_params['flags'] = pygame.FULLSCREEN
        if background is None:
            background = (155,155,155)
        self.background = self.default_background = parse_colour(background)

    def initialize(self):
        pygame.init()
        self.screen = pygame.display.set_mode(**self.display_params)

    def draw_rect(self, adapter: RectAdapter):
        return pygame.draw.rect(
            self.screen, 
            adapter.colour, 
            pygame.Rect(*adapter.rect)
        )
    def draw_circle(self, adapter: CircleAdapter):
        return pygame.draw.circle(
            self.screen,
            adapter.colour,
            adapter.position,
            adapter.size
        )
    def draw_image(self, adapter: ImageAdapter):
        image = adapter.image
        pyg_image = pygame.image.frombytes(
            image.tobytes(),
            image.size,
            image.mode
        )
        pyg_image = pygame.transform.scale(
            pyg_image,
            adapter.size
        )
        return self.screen.blit(pyg_image, adapter.top_left)

    def clear(self):
        self.screen.fill(self.background)
    
    def set_background(self, colour: Optional[str | Sequence[int]]=None):
        if colour is None:
            colour = self.default_background
        self.background = parse_colour(colour)
        self.clear()
        self.flip()

    def flip(self):
        pygame.display.flip()

