from dataclasses import dataclass
from typing import Tuple, Optional


class Event:
    pass


@dataclass
class MouseDownEvent(Event):
    pos: Tuple[float, float]
    button: int
    do: Optional[str] = None


@dataclass
class MouseUpEvent(Event):
    pos: Tuple[float, float]
    button: int
    do: Optional[str] = None


@dataclass
class MouseDragEvent(Event):
    pos: Tuple[float, float]
    rel: Tuple[float, float]
    buttons: Tuple[int, ...]
    do: Optional[str] = None


@dataclass
class KeyDownEvent(Event):
    key: str
    mod: Optional[str] = None
    do: Optional[str] = None


@dataclass
class QuitEvent(Event):
    do: str = "quit"
