from typing import Optional, Sequence, List
import time
from experiment.manager import Manager
from experiment.task.adapters.BaseAdapter import BaseAdapter

class Scene:
    def __init__(self, 
            manager: Manager, 
            adapter: BaseAdapter, 
            event: Optional[int] = None, 
            aux_adapters: Optional[List[BaseAdapter]] = None,
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
        frame_start_time = time.time()
        self.manager.renderer.set_background(self.background)
        while True:
            last_frame_start_time = frame_start_time
            frame_start_time = time.time()
            tick = frame_start_time - last_frame_start_time

            # get events from the event manager
            events = self.manager.eventmanager.get_events()
            for event in events:
                if event.get('do') == "quit":
                    self.quit = True
                    self.manager.logger.log_event("Quit", {"scene": str(self)})
                    break
                elif event.get('do') == "reward":
                    self.manager.good_monkey(
                        duration=event.get('reward_duration', self.manager.variables['default_reward_duration'])
                    )
                elif event.get('do') == "reward_pulses":
                    self.manager.good_monkey(
                        duration=event.get('reward_duration', self.manager.variables['default_reward_duration']),
                        n_pulses=event.get('key'),
                        interpulse_interval=.2
                    )

            # wipe the screen
            self.manager.renderer.clear()
            # update and render the main adapter
            self.adapter.update(tick, events)
            self.adapter.render(self.manager.renderer)
            # update and render auxiliary adapters
            active_aux_adapters = [adapter for adapter in self.aux_adapters if adapter.active]
            for adapter in active_aux_adapters:
                adapter.update(tick, events)
            for adapter in active_aux_adapters:
                adapter.render(self.manager.renderer)
            # update display
            self.manager.renderer.flip()

            # manage frame timing
            render_time = time.time() - frame_start_time
            if render_time > self.manager.frame_duration:
                self.manager.logger.log_event(
                    "FrameDelay",
                    {
                        "render_time": render_time,
                        "scene": str(self)
                    }
                )
            else:
                #TODO: implement sync/async waiting for next frame?
                time.sleep(self.manager.frame_duration - render_time)

            if self.quit or not self.adapter.active:
                break

        # if the scene reaches conclusion
        # reset the adapters in the chain
        for adapter in [self.adapter] + self.aux_adapters:
            adapter.reset()
        self.manager.renderer.set_background()
