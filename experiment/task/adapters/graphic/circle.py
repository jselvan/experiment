from experiment.task.adapters.graphic.base import GraphicAdapter
from experiment.components.renderer.base import Renderer
from experiment.util.bbox import BBox

class CircleAdapter(GraphicAdapter):
    def render(self, renderer: Renderer):
        renderer.draw_circle(self)
