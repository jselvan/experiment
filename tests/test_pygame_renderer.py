import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from experiment.rendering.primitives import (
    CirclePrimitive, RectanglePrimitive, LinePrimitive, ImagePrimitive, Colour
)
from experiment.engine.pygame.renderer import PygameRenderer


class DummyImage:
    def __init__(self, size=(4, 4), mode='RGB'):
        self._size = size
        self.mode = mode

    def tobytes(self):
        # return a small bytes buffer; mocks accept this
        return b"\x00" * (self._size[0] * self._size[1] * 3)

    @property
    def size(self):
        return self._size


class TestPygameRenderer(unittest.TestCase):

    @patch('experiment.engine.pygame.renderer.pygame')
    def test_initialize_sets_screen_and_caption(self, mock_pygame):
        mock_screen = MagicMock()
        mock_pygame.display.set_mode.return_value = mock_screen

        r = PygameRenderer(size=(640, 480), display=1, fullscreen=False)
        r.initialize()

        mock_pygame.init.assert_called_once()
        mock_pygame.display.set_mode.assert_called_once_with((640, 480), flags=0, display=1)
        mock_pygame.display.set_caption.assert_called_once()
        self.assertIs(r.screen, mock_screen)

    @patch('experiment.engine.pygame.renderer.pygame')
    def test_clear_fills_screen_with_background_colour(self, mock_pygame):
        mock_screen = MagicMock()
        mock_pygame.display.set_mode.return_value = mock_screen

        r = PygameRenderer()
        r.initialize()

        # set a known background colour and call clear
        r.background_colour = Colour(10, 20, 30)
        r.clear()

        mock_screen.fill.assert_called_once_with((10, 20, 30))

    @patch('experiment.engine.pygame.renderer.pygame')
    def test_flip_and_get_subject_screen(self, mock_pygame):
        mock_screen = MagicMock()
        mock_pygame.display.set_mode.return_value = mock_screen

        # pixels3d should return a numpy array; ensure a copy is returned by get_subject_screen
        arr = np.zeros((10, 10, 3), dtype=np.uint8)
        mock_pygame.surfarray.pixels3d.return_value = arr

        r = PygameRenderer()
        r.initialize()
        r.flip()

        got = r.get_subject_screen()
        self.assertTrue((got == arr).all())
        self.assertIsNot(got, arr)

    @patch('experiment.engine.pygame.renderer.pygame')
    def test_render_dispatches_to_draw_and_image(self, mock_pygame):
        mock_screen = MagicMock()
        mock_pygame.display.set_mode.return_value = mock_screen

        # prepare draw and image/transform mocks
        mock_pygame.image.frombytes.return_value = MagicMock()
        mock_pygame.transform.scale.return_value = mock_pygame.image.frombytes.return_value
        mock_pygame.transform.rotate.return_value = mock_pygame.image.frombytes.return_value

        r = PygameRenderer()
        r.initialize()

        circle = CirclePrimitive(center=(50, 50), radius=10, edgecolour=Colour(1, 2, 3), facecolour=Colour(4, 5, 6), linewidth=2)
        rect = RectanglePrimitive(center=(20, 20), width=10, height=8, edgecolour=Colour(7, 8, 9), facecolour=None, linewidth=1, orientation=0)
        line = LinePrimitive(start=(0, 0), end=(10, 10), colour=Colour(2, 3, 4), linewidth=1)
        img = DummyImage(size=(8, 8), mode='RGB')
        image_prim = ImagePrimitive(center=(30, 30), width=8, height=8, imagedata=img, orientation=45)

        r.render([circle, rect, line, image_prim])

        # circle: face + edge => draw.circle should have been used
        self.assertTrue(mock_pygame.draw.circle.called)
        # rectangle draw
        self.assertTrue(mock_pygame.draw.rect.called)
        # line draw
        mock_pygame.draw.line.assert_called_once()
        # image path: frombytes -> scale -> rotate -> blit
        mock_pygame.image.frombytes.assert_called_once()
        mock_pygame.transform.scale.assert_called_once()
        mock_screen.blit.assert_called()


if __name__ == '__main__':
    unittest.main()
