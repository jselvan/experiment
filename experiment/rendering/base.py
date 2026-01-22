from experiment.components import BaseComponent
from experiment.rendering.primitives import Primitive, Colour
from typing import Generator, Iterable, Optional, Tuple, Dict
import threading
from collections import ChainMap
from abc import ABC, abstractmethod

import numpy as np

class Adapter(ABC):
    @abstractmethod
    def get_primitives(self) -> Generator[Primitive, None, None]: ...


class BaseRenderer(BaseComponent):
    DEFAULT_BACKGROUND_COLOURS = {
        "pause": Colour.from_string("black"),
        "experiment": Colour.from_string("white"),
    }
    DEFAULT_SIZE = (800, 600)

    def __init__(
        self,
        display: int = 0,
        size: Optional[Tuple[int, int]] = None,
        fullscreen: bool = False,
        background_colours: Optional[Dict[str, Colour]] = None,
    ):
        super().__init__()
        self.display = display
        if size is None:
            size = self.DEFAULT_SIZE
        self.size = size
        self.fullscreen = fullscreen
        self.background_colours = ChainMap(
            background_colours or {}, self.DEFAULT_BACKGROUND_COLOURS
        )
        self.background_colour: Colour = self.background_colours["experiment"]
        self._frame_ready = threading.Condition()
        self._last_frame: Optional[np.ndarray] = None

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the rendering component."""
        ...

    @abstractmethod
    def render(self, primitives: Iterable[Primitive]) -> None:
        """Draw all primitives for the current frame."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear the current frame."""
        ...

    @abstractmethod
    def _flip(self) -> None:
        """Internal method to display the current frame."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the rendering component and free resources."""
        ...
    
    @abstractmethod
    def _get_last_frame(self) -> None:
        """Internal method to capture the last rendered frame."""
        ...

    def flip(self) -> None:
        """Display the current frame and prepare for the next frame."""
        self._flip()
        with self._frame_ready:
            self._get_last_frame()
            self._frame_ready.notify_all()

    def set_background_colour(self, colour: Optional[Colour]):
        """Set the background colour for the renderer."""
        if colour is None:
            colour = self.background_colours["experiment"]
        self.background_colour = colour
        self.clear()
        self.flip()

    def get_subject_screen(self) -> np.ndarray:
        with self._frame_ready:
            if self._last_frame is None:
                self._get_last_frame()
            assert self._last_frame is not None
            return self._last_frame.copy()