from pathlib import Path

class DataStore:
    def __init__(self) -> None:
        self.trialid = 0
        self.session_directory = Path('.')
    def flush(self) -> None:
        pass
    def close(self) -> None:
        pass
    def record(self, **kwargs) -> None:
        pass
