from experiment.experiments.adapters.graphic.base import GraphicAdapter
from experiment.renderers.base import Renderer

class CircleAdapter(GraphicAdapter):
    def render(self, renderer: Renderer):
        renderer.draw_circle(self)
