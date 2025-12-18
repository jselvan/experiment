from typing import Any, Dict
from pathlib import Path

import yaml

from experiment.util.python_import_helper import load_object_from_module

def load_config(config: str | Path) -> Dict[str, Any]:
    config = Path(config).expanduser()
    if config.suffix in {'.yml', '.yaml'}:
        with open(config, 'r') as f:
            cfg = yaml.safe_load(f)
    elif config.suffix == '.py':
        cfg = load_object_from_module(config, 'config')
    else:
        raise ValueError("Unsupported config file type: {}".format(config.suffix))
    return cfg