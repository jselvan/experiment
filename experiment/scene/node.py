from typing import Optional, List, Dict
from abc import ABC, abstractmethod


class Node(ABC):
    """Base node in the scene/control graph.

    A node executes with access to the `Runtime` and returns the next node to run
    (or None to stop the scene).
    """

    def start(self, runtime) -> None:
        """Called once when the node becomes active."""
        return None

    @abstractmethod
    def step(self, runtime) -> Optional["Node"] | str | bool:
        """Run a single step/frame of the node.

        Return values:
        - None: still running
        - True: finished normally (continue to next node in sequence)
        - `str` or `Node`: finished with outcome (propagate)
        """
        ...

    def stop(self, runtime) -> None:
        """Called once when the node is stopped."""
        return None

    def set_background_colour(self, runtime, colour) -> None:
        """Helper for nodes to set the renderer background colour."""
        runtime.renderer.set_background_colour(colour)


class SequenceNode(Node):
    def __init__(self, children: List[Node]):
        self.children = children
        self._index = 0
        self._started = False

    def start(self, runtime) -> None:
        self._index = 0
        self._started = True
        if self.children:
            self.children[0].start(runtime)

    def step(self, runtime):
        if not self.children:
            return True
        child = self.children[self._index]
        res = child.step(runtime)
        if res is None:
            return None
        # child finished
        if res is True:
            # move to next child
            self._index += 1
            if self._index >= len(self.children):
                return True
            self.children[self._index].start(runtime)
            return None
        # child returned Node or str -> propagate
        return res


class AdapterNode(Node):
    """Node that registers an adapter with the runtime for the duration of its run.

    The `adapter` must implement `get_primitives()` returning an Iterable[Primitive]
    for the current frame when called by the runtime.
    """

    def __init__(self, adapter, duration: float):
        self.adapter = adapter
        self.duration = duration
        self._end_time = None
        self._started = False

    def start(self, runtime) -> None:
        self._started = True
        if self.adapter is not None:
            runtime.add_adapter(self.adapter)
        self._end_time = runtime.time() + self.duration

    def step(self, runtime):
        if not self._started:
            self.start(runtime)
        if runtime.time() >= self._end_time:
            if self.adapter is not None:
                runtime.remove_adapter(self.adapter)
            return True
        return None


class TouchNode(Node):
    """Present adapters and wait for touch events.

    adapters: list of (adapter, label) pairs. Each adapter should implement
    `contains_point((x,y)) -> bool`.

    On a touch, the node checks adapters in order; if one contains the touch,
    it returns the associated label or the mapped Node from `outcome_map`.
    If no adapter matches and `ignore_outside_touch` is True the node continues
    waiting; otherwise it returns the `outside_label` or mapped node.
    """

    def __init__(self, adapter_label_pairs, timeout: float, ignore_outside_touch: bool, outcome_map: Optional[Dict[str, Node]] = None, outside_label: str = 'error'):
        # adapter_label_pairs: iterable of (adapter, label)
        self.pairs = list(adapter_label_pairs)
        self.timeout = timeout
        self.ignore_outside_touch = ignore_outside_touch
        self.outcome_map = outcome_map or {}
        self.outside_label = outside_label
        self._started = False
        self._deadline = None
        self._events: List[object] = []
        self._subscribed = False

    def start(self, runtime) -> None:
        self._started = True
        self._deadline = runtime.time() + self.timeout
        # register adapters
        for adapter, _ in self.pairs:
            runtime.add_adapter(adapter)

        # subscribe to event bus to collect MouseDownEvent instances
        def _handler(ev):
            from experiment.events.types import MouseDownEvent
            try:
                if isinstance(ev, MouseDownEvent):
                    self._events.append(ev)
            except Exception:
                return

        runtime.event_bus.subscribe(_handler)
        self._event_handler = _handler
        self._subscribed = True

    def step(self, runtime) -> Optional[Node] | str | bool:
        if not self._started:
            self.start(runtime)

        # process queued events
        while self._events:
            ev = self._events.pop(0)
            from experiment.events.types import MouseDownEvent
            assert isinstance(ev, MouseDownEvent)
            pos = (float(ev.pos[0]), float(ev.pos[1]))
            # check adapters in order for hit
            hit_label = None
            for adapter, label in self.pairs:
                try:
                    if hasattr(adapter, 'contains_point') and adapter.contains_point(pos):
                        hit_label = label
                        break
                except Exception:
                    continue

            if hit_label is None:
                if self.ignore_outside_touch:
                    continue
                if self.outside_label in self.outcome_map:
                    # cleanup
                    self._cleanup(runtime)
                    return self.outcome_map[self.outside_label]
                self._cleanup(runtime)
                return self.outside_label

            # matched an adapter
            if hit_label in self.outcome_map:
                node = self.outcome_map[hit_label]
                self._cleanup(runtime)
                return node
            self._cleanup(runtime)
            return hit_label

        # check for timeout
        if runtime.time() >= self._deadline:
            if 'timeout' in self.outcome_map:
                node = self.outcome_map['timeout']
                self._cleanup(runtime)
                return node
            self._cleanup(runtime)
            return 'timeout'

        return None

    def _cleanup(self, runtime):
        # remove adapters and unsubscribe
        for adapter, _ in self.pairs:
            try:
                runtime.remove_adapter(adapter)
            except Exception:
                pass
        if self._subscribed:
            try:
                runtime.event_bus.unsubscribe(self._event_handler)
            except Exception:
                pass
            self._subscribed = False


class OutcomeNode(Node):
    """Set a background colour and wait for a duration, then continue."""

    def __init__(self, colour, duration: float):
        self.colour = colour
        self.duration = duration
        self._deadline = None
        self._started = False

    def start(self, runtime) -> None:
        self._started = True
        runtime.renderer.set_background_colour(self.colour)
        self._deadline = runtime.time() + self.duration

    def step(self, runtime):
        if not self._started:
            self.start(runtime)
        if runtime.time() >= self._deadline:
            return True
        return None
