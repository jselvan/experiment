from experiment.manager import Manager
from experiment.task.trial import BaseTrial
from experiment.task.scene import Scene
from experiment.task.adapters import *
from typing import Dict

class Trial(BaseTrial):
    def __init__(self, timings: Dict[str, float], x: int, y: int, s: int, **kwargs):
        super().__init__(timings=timings, **kwargs)
        self.x = x
        self.y = y
        self.s = s
    
    def run(self, mgr: Manager) -> bool:
        crc = CircleAdapter(
            position=(self.x, self.y),
            size=self.s,
            colour='RED',
            bbox={'width': self.s, 'height': self.s}
        )
        ta = TouchAdapter(
            time_counter=5,
            items={'circle': crc}
        )
        scene = Scene(mgr, ta)
        scene.run()
        mgr.record(correct=ta.chosen)
        return not scene.quit