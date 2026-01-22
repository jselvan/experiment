from typing import Dict, Callable


class HotkeyRegistry:
    """Registry that attaches actions to keydown events by modifying event.do.

    It subscribes to an EventBus-compatible publish/subscribe interface (callable handlers).
    """

    def __init__(self, bus):
        self._bus = bus
        # map from string key identifier (e.g., 'q', 'ctrl+q') to action
        self._map: Dict[str, str] = {}
        self._bus.subscribe(self._handler)

    def register_key(self, key_id: str, action: str) -> None:
        """Register a key identifier (string) to an action.

        The `key_id` should match the `KeyDownEvent.key` string produced by
        event sources (for pygame this is `pygame.key.name(event.key)`).
        """
        self._map[key_id] = action

    def unregister_key(self, key_id: str) -> None:
        if key_id in self._map:
            del self._map[key_id]

    def _handler(self, ev):
        # import locally to avoid circular imports at module import time
        from experiment.events.types import KeyDownEvent
        try:
            if isinstance(ev, KeyDownEvent):
                # ev.key is a string key id
                action = self._map.get(ev.key)
                if action:
                    ev.do = action
        except Exception:
            return

    def close(self):
        try:
            self._bus.unsubscribe(self._handler)
        except Exception:
            pass
