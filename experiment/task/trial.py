from typing import Dict

class BaseTrial:
    def __init__(self, timings: Dict[str, float], **kwargs):
        self.timings = timings
    def set_iti(self, iti: float):
        self.timings['iti'] = iti
    