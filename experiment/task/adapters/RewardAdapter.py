from experiment.manager import Manager
from experiment.task.adapters import BaseAdapter, TimeCounter, ProgressBarAdapter
from experiment.components.renderer.base import Renderer
from experiment.components.events import Event
from typing import Sequence

class RewardAdapter(BaseAdapter):
    def __init__(self, 
        duration: float,
        n_pulses: int = 1,
        interpulse_interval: float | None = None,
        **kwargs):
        children = kwargs.pop('children', [])
        super().__init__(children=children)
        self.reward_setup_callback = kwargs.pop('reward_setup_callback', lambda: None)
        self.reward_on_callback = kwargs.pop('reward_on_callback', lambda: None)
        self.reward_off_callback = kwargs.pop('reward_off_callback', lambda: None)

        if interpulse_interval is None:
            interpulse_interval = duration

        progress_params = kwargs.get('progress_params', {})
        progress_center = progress_params.get('position', (100, 100))
        progress_size = progress_params.get('size', (200, 30))
        progress_colour = progress_params.get('colour', (0, 255, 0))
        progress_gap = progress_params.get('gap', 10)
        total_height = n_pulses * progress_size[1] + (n_pulses - 1) * progress_gap
        progress_topleft = progress_center[0] - progress_size[0] // 2, progress_center[1] - total_height // 2
        offset = progress_size[1] + progress_gap

        self.timecounters = []
        for pulse in range(n_pulses):
            position = (progress_topleft[0], progress_topleft[1] + pulse * offset)
            self.timecounters.append(
                TimeCounter(duration, 
                    on_enter=self.reward_on_callback, 
                    on_exit=self.reward_off_callback, 
                    children=[ProgressBarAdapter(
                        position=position,
                        size=progress_size,
                        colour=progress_colour,
                        duration=duration
                    )]
                )
            )
            if pulse < n_pulses - 1:
                self.timecounters.append(
                    TimeCounter(interpulse_interval)
                )
    
    @classmethod
    def from_manager(cls, manager: "Manager", duration, n_pulses, interpulse_interval, **kwargs) -> "RewardAdapter":
        speed = kwargs.pop('speed', None)
        channels = kwargs.pop('channels', None)
        reward_callbacks = manager.iointerface.get_reward_callbacks(speed=speed, channels=channels)
        return cls(
            duration=duration,
            n_pulses=n_pulses,
            interpulse_interval=interpulse_interval,
            reward_setup_callback=reward_callbacks['reward_setup_callback'],
            reward_on_callback=reward_callbacks['reward_on_callback'],
            reward_off_callback=reward_callbacks['reward_off_callback'],
            **kwargs
        )


    def start(self):
        super().start()
        self.reward_setup_callback()
        self.timecounter_index = 0
        self.timecounters[self.timecounter_index].start()
    
    @property
    def current_timecounter(self) -> TimeCounter | None:
        if self.timecounter_index >= len(self.timecounters):
            return None
        return self.timecounters[self.timecounter_index]

    def update(self, tick: float, events: Sequence["Event"]) -> bool:
        if self.current_timecounter is None:
            self.active = False
            return False

        if self.current_timecounter.update(tick, events):
            return True

        # Move to the next time counter if the current one is done
        self.timecounter_index += 1
        if self.timecounter_index < len(self.timecounters):
            self.timecounters[self.timecounter_index].start()
            return True

        self.active = False
        return False
    
    def render(self, renderer: "Renderer"):
        for child in self.timecounters:
            child.render(renderer)
    
    def reset(self):
        super().reset()
        for child in self.timecounters:
            child.reset()