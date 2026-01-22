from experiment.rendering.base import BaseRenderer
from experiment.rendering.primitives import (
    Colour, Primitive, CirclePrimitive, RectanglePrimitive, LinePrimitive, ImagePrimitive
)

import pygame

class PygameRenderer(BaseRenderer):
    DEFAULT_CAPTION = "Experiment Renderer"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen: pygame.Surface | None = None

    def initialize(self) -> None:
        pygame.init()
        flags = 0
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(
            self.size, 
            flags=flags,
            display=self.display,
        )
        pygame.display.set_caption(self.DEFAULT_CAPTION)

    def render(self, primitives):
        for primitive in primitives:
            if isinstance(primitive, CirclePrimitive):
                self._render_circle(primitive)
            elif isinstance(primitive, RectanglePrimitive):
                self._render_rectangle(primitive)
            elif isinstance(primitive, LinePrimitive):
                self._render_line(primitive)
            elif isinstance(primitive, ImagePrimitive):
                self._render_image(primitive)
            else:
                raise ValueError(f"Unknown primitive type: {type(primitive)}")
    
    def clear(self) -> None:
        if self.screen is None:
            raise RuntimeError("Renderer not initialized.")
        self.screen.fill(self.background_colour.to_tuple())
    
    def _flip(self) -> None:
        if self.screen is None:
            raise RuntimeError("Renderer not initialized.")
        pygame.display.flip()
    
    def close(self) -> None:
        pygame.quit()
    
    def _get_last_frame(self) -> None:
        if self.screen is None:
            raise RuntimeError("Renderer not initialized.")
        self._last_frame = pygame.surfarray.pixels3d(self.screen)

    def _render_circle(self, primitive: CirclePrimitive):
        if self.screen is None:
            raise RuntimeError("Renderer not initialized.")
        # draw a circle with the appropriate facecolour and edgecolour
        if primitive.facecolour:
            pygame.draw.circle(
                self.screen,
                primitive.facecolour.to_tuple() if primitive.facecolour else (0, 0, 0, 0),
                (int(primitive.center[0]), int(primitive.center[1])),
                primitive.radius,
                0
            )
        if primitive.edgecolour:
            pygame.draw.circle(
                self.screen,
                primitive.edgecolour.to_tuple(),
                (int(primitive.center[0]), int(primitive.center[1])),
                primitive.radius,
                int(primitive.linewidth)
            )

    def _render_rectangle(self, primitive: RectanglePrimitive):
        if self.screen is None:
            raise RuntimeError("Renderer not initialized.")
        rect = pygame.Rect(
            int(primitive.center[0] - primitive.width / 2),
            int(primitive.center[1] - primitive.height / 2),
            int(primitive.width),
            int(primitive.height)
        )
        if primitive.facecolour:
            pygame.draw.rect(
                self.screen,
                primitive.facecolour.to_tuple(),
                rect,
                0
            )
        if primitive.edgecolour:
            pygame.draw.rect(
                self.screen,
                primitive.edgecolour.to_tuple(),
                rect,
                int(primitive.linewidth)
            )

    def _render_line(self, primitive: LinePrimitive):
        if self.screen is None:
            raise RuntimeError("Renderer not initialized.")
        pygame.draw.line(
            self.screen,
            primitive.colour.to_tuple(),
            (int(primitive.start[0]), int(primitive.start[1])),
            (int(primitive.end[0]), int(primitive.end[1])),
            int(primitive.linewidth)
        )

    def _render_image(self, primitive: ImagePrimitive):
        if self.screen is None:
            raise RuntimeError("Renderer not initialized.")
        image = primitive.imagedata
        pyg_image = pygame.image.frombytes(
            image.tobytes(),
            image.size,
            image.mode #type: ignore
        )
        pyg_image = pygame.transform.scale(
            pyg_image,
            (int(primitive.width), int(primitive.height))
        )
        if primitive.orientation != 0:
            pyg_image = pygame.transform.rotate(pyg_image, primitive.orientation)
        rect = pyg_image.get_rect(center=(int(primitive.center[0]), int(primitive.center[1])))
        self.screen.blit(pyg_image, rect)