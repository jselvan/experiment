from __future__ import annotations
import time
from typing import Callable, Optional


class Clock:
    """Clock abstraction to run a frame loop at a fixed fps.

    Use `run_for(duration, step)` to run for `duration` seconds, calling
    `step()` once per frame. `time()` returns the current monotonic time.
    """

    def __init__(self, fps: int = 60):
        self.fps = fps
        self._frame_time = 1.0 / fps

    def time(self) -> float:
        return time.time()

    @property
    def frame_time(self) -> float:
        """Seconds per frame at the configured FPS."""
        return self._frame_time
    
    def sleep(self, duration: float) -> None:
        """Sleep for the given duration in seconds."""
        time.sleep(duration)
