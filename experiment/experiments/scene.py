from typing import Optional, Sequence
import time
from experiment.manager import Manager
from experiment.experiments.adapters.BaseAdapter import BaseAdapter

class Scene:
    def __init__(self, 
            manager: Manager, 
            adapter: BaseAdapter, 
            event: Optional[int] = None, 
            aux_adapters: Optional[Sequence[BaseAdapter]] = None,
            background: Optional[str | Sequence[int]] = None
        ):
        self.manager = manager
        self.adapter = adapter
        self.event = event
        self.background = background
        if aux_adapters is None:
            aux_adapters = []
        self.aux_adapters = aux_adapters
        self.quit = False
    def run(self):
        #fire off the event at the start of the scene
        if self.event is not None:
            raise NotImplementedError()

        for adapter in [self.adapter] + self.aux_adapters:
            adapter.start()
        frame_end_time = time.time()
        self.manager.renderer.set_background(self.background)
        while True:
            frame_start_time = time.time()
            tick = frame_start_time - frame_end_time
            self.manager.renderer.clear()
            # get events from the event manager
            events = self.manager.eventmanager.get_events()
            for event in events:
                if event.get('do') == "quit":
                    self.quit = True
                    self.manager.logger.log_event("Quit", {"scene": str(self)})
                    break
            # update the main adapter
            self.adapter.update(tick, events)
            self.adapter.render(self.manager.renderer)

            active_aux_adapters = [adapter for adapter in self.aux_adapters if adapter.active]
            for adapter in active_aux_adapters:
                adapter.update(tick, events)
            for adapter in active_aux_adapters:
                adapter.render(self.manager.renderer)

            self.manager.renderer.flip()
            frame_end_time = time.time()
            elapsed = frame_end_time - frame_start_time
            if elapsed > self.manager.frame_duration:
                self.manager.logger.log_event(
                    "FrameDelay",
                    {
                        "elapsed_time": elapsed,
                        "scene": str(self)
                    }
                )
            else:
                #TODO: implement sync/async waiting for next frame?
                time.sleep(self.manager.frame_duration - elapsed)

            if self.quit or not self.adapter.active:
                break

        # if the scene reaches conclusion
        # reset the adapters in the chain
        for adapter in [self.adapter] + self.aux_adapters:
            adapter.reset()
        self.manager.renderer.set_background()
