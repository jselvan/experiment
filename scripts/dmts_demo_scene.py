"""Delayed Match-to-Sample example using the scene/node framework and Runtime.

Behavior:
- Present red circle for 1s
- Blank for 2s
- Present red circle and blue square for up to 5s waiting for a touch
- If red selected -> green correct screen
- If blue selected -> red error screen
- If timeout -> grey timeout screen
"""
from experiment.scene.node import SequenceNode, AdapterNode, TouchNode, OutcomeNode
from experiment.scene.adapters import CircleAdapter, RectAdapter
from experiment.runtime import Runtime
from experiment.rendering.primitives import Colour


def make_scene():
    # adapters
    red = CircleAdapter(center=(320,240), radius=40, facecolour=Colour(255,0,0), bbox={'radius': 50})
    blue = RectAdapter(center=(420,240), width=80, height=80, facecolour=Colour(0,0,255), bbox={'radius': 50})

    correct_node = OutcomeNode(Colour(0,255,0), duration=1.0)
    error_node = OutcomeNode(Colour(255,0,0), duration=1.0)
    timeout_node = OutcomeNode(Colour(128,128,128), duration=1.0)

    nodes = [
        AdapterNode(adapter=red, duration=1.0),  # sample
        AdapterNode(adapter=None, duration=2.0),  # blank
        TouchNode(
            adapter_label_pairs=[(red, 'correct'), (blue, 'error')],
            timeout=5.0,
            ignore_outside_touch=True,
            outcome_map={'correct': correct_node, 'error': error_node, 'timeout': timeout_node},
        ),
    ]

    return SequenceNode(nodes)


def run():
    from experiment.engine.pygame.renderer import PygameRenderer
    from experiment.engine.pygame.events import PygameEventSource

    renderer = PygameRenderer()
    rt = Runtime(renderer=renderer)
    evt_src = PygameEventSource()
    rt.add_event_source(evt_src)

    start = make_scene()
    rt.run_scene(start)


if __name__ == '__main__':
    run()
