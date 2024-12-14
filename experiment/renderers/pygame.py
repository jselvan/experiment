import pygame
from experiment.renderers.base import Renderer
from experiment.experiments.adapters.GraphicAdapter import RectAdapter, CircleAdapter

class PygameRenderer(Renderer):
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.background = (155,155,155)

    def initialize(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size)

    def draw_rect(self, adapter: "RectAdapter"):
        return pygame.draw.rect(
            self.screen, 
            adapter.colour, 
            pygame.Rect(*adapter.rect)
        )
    def draw_circle(self, adapter: "CircleAdapter"):
        return pygame.draw.circle(
            self.screen,
            adapter.colour,
            adapter.position,
            adapter.size
        )

    def clear(self):
        self.screen.fill(self.background)

    def flip(self):
        pygame.display.flip()

