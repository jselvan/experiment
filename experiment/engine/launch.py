from pathlib import Path
import os
import tomllib
import importlib

config_dir = Path(os.environ.get('EXPERIMENT_CONFIG_PATH', '~/.experiment')).expanduser().resolve()
if not (config_dir/'config.toml').exists():
    raise FileNotFoundError(f'No configuration file found at {config_dir/"config.toml"}')

config_file = config_dir/'config.toml'
with open(config_file, 'rb') as f:
    config = tomllib.load(f)

engine = config.get('engine', 'base')
if engine == 'pygame':
    assert 'display' in config, 'No "display" section found in configuration file'
    config['display']['type'] = 'pygame'
    config['events'] = config.setdefault('events', {'type': 'pygame'})

from experiment.manager import Manager
manager_cls = Manager

if 'display' in config:
    display_params = config['display']
    display_type = display_params.pop('type', None)
    if display_type == 'pygame':
        display_params['module'] = 'experiment.renderers.pygame'
        display_params['class'] = 'PygameRenderer'

    renderer_module_name = display_params.pop('module', None)
    if renderer_module_name is None:
        raise ValueError('No "type" or "module" specified for display')
    renderer_module = importlib.import_module(renderer_module_name)
    renderer_cls = getattr(renderer_module, display_params.pop('class'), None)
    if renderer_cls is None:
        raise ValueError(f'No class "{display_params["class"]}" found in module "{display_params["module"]}"')
    display_cls = renderer_cls(display_params)

if 'events' in config:
    events_params = config['events']
    events_type = events_params.pop('type', None)
    if events_type == 'pygame':
        events_params['module'] = 'experiment.events.pygame'
        events_params['class'] = 'PygameEventManager'

    events_module_name = events_params.pop('module', None)
    if events_module_name is None:
        raise ValueError('No "type" or "module" specified for events')
    events_module = importlib.import_module(events_module_name)
    events_cls = getattr(events_module, events_params.pop('class'), None)
    if events_cls is None:
        raise ValueError(f'No class "{events_params["class"]}" found in module "{events_params["module"]}"')
    events_handler = events_cls(events_params)

# else:
#     from experiment.manager import Manager
#     manager_cls = Manager

if 'io' in config:
    io_config = config['io']
    io_module = importlib.import_module(io_config.get('module', 'experiment.io.base'))
    io_cls = getattr(io_module, io_config.get('class', 'IOInterface'), None)
    if io_cls is None:
        raise ValueError(f'No class "{io_config["class"]}" found in module "{io_config["module"]}"')
    io_cls = io_cls()

    for device_name, device_config in io_config.get('devices', {}).items():
        device_type = device_config.get('type')
        if device_type is None:
            raise ValueError(f'No "type" specified for device "{device_name}"')
        elif device_type == 'ISMATEC_SERIAL':
            device_address = device_config.get('address')
            if device_address is None:
                raise ValueError(f'No "address" specified for device "{device_name}"')
            from experiment.io.ismatec import IsmatecPumpSerial
            device = IsmatecPumpSerial(device_address)
            channel_info = device_config.get('channels', [])
            device.init(channel_info)
            io_cls.add_device(device_name, device)
        else:
            raise ValueError(f'Unknown device type "{device_type}" specified for device "{device_name}"')
