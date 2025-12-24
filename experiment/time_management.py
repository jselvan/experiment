from datetime import datetime
from typing import Dict, Any

from experiment.experiments.scene import Scene
from experiment.experiments.adapters import TimeCounter

def check_if_valid_time(config: Dict[str, Any], current_time: datetime) -> bool:
    valid_times = config.get('valid_times', None)
    if valid_times is None:
        return True
    for timerange in valid_times:
        start = datetime.strptime(timerange.get('start', '00:00'), '%H:%M')
        end = datetime.strptime(timerange.get('end', '23:59'), '%H:%M')
        if start.hour <= current_time.hour < end.hour:
            return True
    else:
        return False

def get_pause_scene(manager):
    scene = Scene(manager, adapter=TimeCounter(60), background=(0,0,0))
    return scene