from collections.abc import Sequence
from experiment.experiments.adapters import BaseAdapter

class Scene:
    def __init__(self, adapter: BaseAdapter, event: int | None, aux_adapters: Sequence[BaseAdapter] | None):
        self.adapter = adapter
        self.event = event
        if aux_adapters is None:
            aux_adapters = []
        self.aux_adapters = aux_adapters
    def run(self):
        #fire off the event at the start of the scene
        if self.event is not None:
            raise NotImplemented()

        while True:
            # update the main adapter
            self.adapter.update()
            # if still active, render the adapter chain
            # else kill the scene
            if self.adapter.active:
                self.adapter.render()
            else:
                break

            # if still active, update and render the active aux adapters
            active_aux_adapters = [adapter for adapter in self.aux_adapters if adapter.active]
            for adapter in active_aux_adapters:
                adapter.update()
            for adapter in active_aux_adapters:
                adapter.render()


