from experiment.experiments.adapters.BaseAdapter import BaseAdapter
class Renderer: 
    def initialize(self): raise NotImplementedError()
    def draw_rdm(self, adapter: BaseAdapter): raise NotImplementedError()
    def draw_rect(self, adapter: BaseAdapter): raise NotImplementedError()
    def draw_circle(self, adapter: BaseAdapter): raise NotImplementedError()
