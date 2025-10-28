import unittest
import pygame
class TestPygame(unittest.TestCase):
    def setUp(self) -> None:
        from experiment.components.renderer.pygame import PygameRenderer
        self.renderer = PygameRenderer(
            display_params={
                "size": (800, 600)
            }
        )
        self.renderer.initialize()
    def test_render_circle(self):
        from experiment.task.adapters.graphic.circle import CircleAdapter
        circle = CircleAdapter(
            position=[400, 300],
            size=50,
            colour='RED'
        )
        self.renderer.clear()
        circle.render(self.renderer)
        self.renderer.flip()
        pygame.time.delay(1000)  # Display for 1 second
    def test_render_rect(self):
        from experiment.task.adapters.graphic.rect import RectAdapter
        rect = RectAdapter(
            position=[400, 300],
            size=[200, 100],
            colour='BLUE'
        )
        self.renderer.clear()
        rect.render(self.renderer)
        self.renderer.flip()
        pygame.time.delay(1000)  # Display for 1 second
    def test_render_image(self):
        from experiment.task.adapters.graphic.image import ImageAdapter
        from PIL import Image
        image = Image.new('RGB', (100, 100), (0, 255, 0))  # Create a green square
        img_adapter = ImageAdapter(
            image=image,
            position=[400, 300],
            size=[100, 100]
        )
        self.renderer.clear()
        img_adapter.render(self.renderer)
        self.renderer.flip()
        pygame.time.delay(1000)  # Display for 1 second
    def tearDown(self) -> None:
        pygame.quit()