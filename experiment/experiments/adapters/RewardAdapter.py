from experiment.experiments.adapters.BaseAdapter import BaseAdapter
from experiment.experiments.adapters.TimeCounter import TimeCounter
from experiment.experiments.adapters.ProgressBarAdapter import ProgressBarAdapter
from experiment.renderers.base import Renderer
from experiment.events import Event
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

        progress_params = kwargs.get('progress_params', {})
        progress_topleft = progress_params.get('position', (100, 100))
        progress_size = progress_params.get('size', (200, 30))
        progress_color = progress_params.get('color', (0, 255, 0))
        progress_gap = progress_params.get('gap', 10)
        offset = progress_size[1] + progress_gap

        self.timecounters = []
        for pulse in range(n_pulses):
            position = (progress_topleft[0], progress_topleft[1] + pulse * offset)
            self.timecounters.append(
                TimeCounter(duration, 
                    on_start=self.reward_on_callback, 
                    on_complete=self.reward_off_callback, 
                    children=[ProgressBarAdapter(
                        position=position,
                        size=progress_size,
                        colour=progress_color,
                        duration=duration
                    )],
                    name=f"Reward Pulse {pulse+1}"
                )
            )
            if interpulse_interval is not None and pulse < n_pulses - 1:
                self.timecounters.append(
                    TimeCounter(interpulse_interval)
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