from __future__ import annotations
from typing import List, Iterable, Optional, Tuple, Callable

from experiment.rendering.primitives import Primitive
from experiment.rendering.base import BaseRenderer, Adapter
from experiment.events.bus import EventBus
from experiment.events.base import EventSource
from experiment.clock import Clock
from experiment.events.hotkeys import HotkeyRegistry
import threading


class Runtime:
    """Runtime that drives rendering, timing and input via an EventBus and Clock.

    Adapters supply primitives via `get_primitives()`; EventSources are polled
    each frame and publish events onto the `EventBus`.
    """

    def __init__(self, renderer: BaseRenderer, fps: int = 60, event_bus: Optional[EventBus] = None):
        self.renderer = renderer
        self.adapters: List[Adapter] = []
        self.event_bus = event_bus or EventBus()
        self.event_sources: List[EventSource] = []
        self.clock = Clock(fps)
        # create a hotkey registry and register Q -> quit by default
        self._hotkeys = HotkeyRegistry(self.event_bus)
        self._hotkeys.register_key('q', 'quit')
        # flag set when a quit action is requested
        self._should_quit = False
        # subscribe to bus to catch actions (do == 'quit')
        def _action_handler(ev):
            self._should_quit = 'quit'

        self._action_handler = _action_handler
        self.event_bus.subscribe(self._action_handler, action='quit')

    def time(self) -> float:
        return self.clock.time()

    def add_adapter(self, adapter: Adapter) -> None:
        if adapter not in self.adapters:
            self.adapters.append(adapter)

    def remove_adapter(self, adapter: Adapter) -> None:
        if adapter in self.adapters:
            self.adapters.remove(adapter)

    def add_event_source(self, source: EventSource) -> None:
        if source not in self.event_sources:
            source.set_bus(self.event_bus)
            self.event_sources.append(source)

    def remove_event_source(self, source: EventSource) -> None:
        if source in self.event_sources:
            self.event_sources.remove(source)

    def _collect_primitives(self) -> List[Primitive]:
        primitives: List[Primitive] = []
        for adapter in list(self.adapters):
            try:
                items = adapter.get_primitives()
                if items:
                    primitives.extend(items)
            except Exception:
                continue
        return primitives

    def _poll_event_sources(self) -> None:
        for src in list(self.event_sources):
            try:
                src.poll()
            except Exception:
                continue

    def render_frame(self) -> None:
        primitives = self._collect_primitives()
        self.renderer.clear()
        self.renderer.render(primitives)
        self.renderer.flip()

    def run_scene(self, start_node) -> None | str:
        self.renderer.initialize()
        final_result = None
        frame_time = self.clock.frame_time
    
        try:
            node = start_node
            if node is None:
                return None
            # call start on the initial node if present
            node.start(self)
            while node is not None:
                if self._should_quit:
                    final_result = 'quit'
                    break

                start = self.time()
                # poll event sources so they publish to the bus
                self._poll_event_sources()
                if self._should_quit:
                    final_result = 'quit'
                    break
                res = node.step(self)
                # interpret result
                if res is None:
                    # still running
                    pass
                elif res is True:
                    # finished normally
                    node = None
                    break
                elif isinstance(res, str):
                    final_result = res
                    break
                else:
                    # assume it's a Node instance to run next
                    node = res
                    node.start(self)

                # render this frame
                self.render_frame()

                # sleep to maintain fps
                elapsed = self.time() - start
                self.clock.sleep(max(0, frame_time - elapsed))
        finally:
            # cleanup
            try:
                self.event_bus.unsubscribe(self._action_handler)
            except Exception:
                pass
            try:
                if self._hotkeys is not None:
                    self._hotkeys.close()
            except Exception:
                pass
            try:
                self.renderer.close()
            except Exception:
                pass
        return final_result
