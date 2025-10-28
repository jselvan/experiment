from experiment.manager import Manager, Logger
from experiment.renderers.pygame import PygameRenderer
from experiment.events.pygame import PygameEventManager

class PygameManager(Manager):
    def __init__(self, data_directory, config):
        display_params = config.pop('display')
        background = config.pop('background', None)
        super().__init__(
            data_directory=data_directory,
            renderer=PygameRenderer(display_params, background),
            logger=Logger(),
            eventmanager=PygameEventManager(self),
            config=config,
            taskmanager=None
        )
        self.renderer.initialize()

if __name__ == '__main__':
    from experiment.experiments.adapters.TimeCounter import TimeCounter
    from experiment.experiments.adapters.GraphicAdapter import RectAdapter, CircleAdapter, ImageAdapter
    from experiment.experiments.adapters.Touch import TouchAdapter
    from experiment.experiments.scene import Scene

    mgr = PygameManager({'screen_size': (1000, 1000)})
    rect = RectAdapter(position=(100, 100), size=(50, 100), colour='WHITE', bbox={'width': 100, 'height': 100})
    crc = CircleAdapter(position=(300, 200), size=25, colour='#ff0000')
    im = ImageAdapter(position=(500, 500), size=(100, 100), image='test/stimuli/aadaa.png')
    tc1 = TimeCounter(duration=10)
    tc2 = TimeCounter(duration=2, children=[crc, im])
    ta = TouchAdapter(
        tc1,
        {'a': rect}
    )
    s1 = Scene(mgr, ta, event=None, aux_adapters=None)
    s2 = Scene(mgr, tc2, event=None, aux_adapters=None)

    s1.run()
    if ta.state == 'correct':
        s2.run()
