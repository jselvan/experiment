from typing import Callable, List, Any, Tuple
import threading


class EventBus:
    """Simple publish/subscribe event bus.

    Subscribers are callables accepting a single `event` argument.
    """

    def __init__(self):
        self._subs: List[Tuple[Callable[[Any], None], None | str]] = []
        self._lock = threading.Lock()

    def subscribe(self, handler: Callable[[Any], None], action: None | str = None) -> None:
        with self._lock:
            if (handler, action) not in self._subs:
                self._subs.append((handler, action))

    def unsubscribe(self, handler: Callable[[Any], None]) -> None:
        with self._lock:
            self._subs = [(h, a) for (h, a) in self._subs if h != handler]

    def publish(self, event: object) -> None:
        # copy subscribers under lock to avoid modification during iteration
        with self._lock:
            subs = list(self._subs)
        for handler, action in subs:
            if event is not None and action is not None:
                # check if event has 'do' attribute matching action
                if not (hasattr(event, 'do') and getattr(event, 'do') == action):
                    continue
            try:
                handler(event)
            except Exception:
                # subscriber errors should not break the bus
                continue