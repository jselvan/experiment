"""Simple demo showing PygameRenderer drawing animated primitives.

Run with:
  uv run .\scripts\demo_pygame_renderer.py
or
  python .\scripts\demo_pygame_renderer.py
"""
import time

from experiment.engine.pygame.renderer import PygameRenderer
from experiment.rendering.primitives import CirclePrimitive, RectanglePrimitive, LinePrimitive, Colour

def main():
    r = PygameRenderer(size=(640, 480))
    r.initialize()

    import pygame
    clock = pygame.time.Clock()

    x = 100
    dx = 3
    running = True
    try:
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    running = False

            r.clear()

            circle = CirclePrimitive(
                center=(x, 240),
                radius=40,
                edgecolour=Colour(255, 255, 255),
                facecolour=Colour(30, 144, 255),
                linewidth=4,
            )

            rect = RectanglePrimitive(
                center=(320, 120),
                width=120,
                height=60,
                edgecolour=None,
                facecolour=Colour(34, 139, 34),
                linewidth=1,
                orientation=0,
            )

            line = LinePrimitive(
                start=(0, 0),
                end=(640, 480),
                colour=Colour(255, 215, 0),
                linewidth=3,
            )

            r.render([rect, line, circle])
            r.flip()

            x += dx
            if x > 600 or x < 40:
                dx = -dx

            clock.tick(60)
    finally:
        r.close()


if __name__ == '__main__':
    main()
