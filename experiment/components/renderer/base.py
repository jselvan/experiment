from experiment.components.components import BaseComponent

from typing import TYPE_CHECKING
import threading

if TYPE_CHECKING:
    from experiment.task.adapters import *

class Renderer(BaseComponent): 
    COMPONENT_TYPE = "renderer"
    def __init__(self):
        super().__init__()
        self._frame_ready = threading.Condition()
    def initialize(self): raise NotImplementedError()
    def draw_image(self, adapter: 'ImageAdapter'): raise NotImplementedError()
    def draw_rect(self, adapter: 'RectAdapter'): raise NotImplementedError()
    def draw_circle(self, adapter: 'CircleAdapter'): raise NotImplementedError()
