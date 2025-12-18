from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class TrialResult:
    continue_session: bool
    outcome: str
    data: Dict[str, Any]

class Trial:
    def run(self, manager) -> TrialResult:
        ...
