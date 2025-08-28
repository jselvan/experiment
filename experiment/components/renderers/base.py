# from experiment.experiments.adapters.BaseAdapter import BaseAdapter
from experiment.components import BaseComponent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from experiment.experiments.adapters.graphic import *

class Renderer(BaseComponent): 
    COMPONENT_TYPE = "renderer"
    def initialize(self): raise NotImplementedError()
    def draw_image(self, adapter: ImageAdapter): raise NotImplementedError()
    def draw_rect(self, adapter: RectAdapter): raise NotImplementedError()
    def draw_circle(self, adapter: CircleAdapter): raise NotImplementedError()
