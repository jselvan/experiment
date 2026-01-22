from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from experiment.experiments.adapters.BaseAdapter import BaseAdapter

class Renderer: 
    def initialize(self): raise NotImplementedError()
    def pause(self): raise NotImplementedError()
    def draw_image(self, adapter: 'BaseAdapter'): raise NotImplementedError()
    def draw_rdm(self, adapter: 'BaseAdapter'): raise NotImplementedError()
    def draw_rect(self, adapter: 'BaseAdapter'): raise NotImplementedError()
    def draw_circle(self, adapter: 'BaseAdapter'): raise NotImplementedError()
    def set_background(self, colour: Optional[str | tuple] = None): raise NotImplementedError()
    def clear(self): raise NotImplementedError()