from experiment.util.config import load_config

from experiment.manager import Manager
from experiment.engine.pygame import PygameManager
from pathlib import Path

default_config = {
    'engine': 'pygame',
    'data_directory': './data',
    'strict_mode': True,
    'display': {
        'size': (800, 600),
        'fullscreen': False,
        'display': 0
    },
    'camera': {
        'device_index': 0,
    },
    'remote': {
        'enabled': True,
        'show': True
    },
    'io': {
        'reward': {
            'type': 'ISMATEC_SERIAL',
            'address': '/dev/ttyACM0',
            'channels': [
                {'channel': '2', 'clockwise': True, 'speed': 100},
                {'channel': '3', 'clockwise': True, 'speed': 100}
            ]
        }
    },
    'valid_times': [
        {'start': '08:00', 'end': '18:00'},
    ]
}

def load_manager(config: dict) -> Manager:
    engine = config.get('engine', 'pygame')
    if engine != 'pygame':
        raise ValueError(f'Unsupported engine: {engine}')
    data_directory = Path(config.get('data_directory', './data'))
    monkey = config.get('name')
    if monkey is not None:
        data_directory = data_directory / monkey
    data_directory.mkdir(parents=True, exist_ok=True)
    # recursively update default_config with config
    def recursive_update(d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = recursive_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    cfg = recursive_update(default_config.copy(), config)
    mgr = PygameManager(data_directory, cfg)
    return mgr

def main(config, **overrides):
    cfg = load_config(config)
    cfg.update(overrides)
    mgr = load_manager(cfg)
    mgr.run_session_from_config(cfg)

if __name__ == "__main__":
    import sys
    config = sys.argv[1]
    config_path = Path(config)
    if not config_path.exists():
        config_paths = list(Path('configs').glob(f'{config}*'))
        if len(config_paths) == 1:
            config = config_paths[0].as_posix()
        else:
            raise ValueError(f'Could not find config {config}')
        
    overrides = {}
    if '--debug' in sys.argv:
        overrides['strict_mode'] = False
        overrides['display'] = {'fullscreen': False}
    elif '--strict' in sys.argv:
        overrides['strict_mode'] = True

    main(config, **overrides)