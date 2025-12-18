from typing import Dict, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from experiment.manager import Manager

@dataclass
class TrialResult:
    continue_session: bool
    outcome: str
    data: Dict[str, Any]

class Trial:
    def run(self, mgr: "Manager") -> TrialResult:
        ...
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "Trial":
        ...
