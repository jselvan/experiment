from collections.abc import Mapping, Sequence
import os
from pathlib import Path
from datetime import datetime

import yaml
import warnings
warnings.simplefilter("always")
from experiment.renderers.base import Renderer
from experiment.taskmanager import TaskManager
from experiment.events import EventManager, Event
from experiment.datastore.base import DataStore
from experiment.datastore.jsonstore import JSONDataStore
from experiment.io.base import IOInterface

class ConfigManager: 
    def __init__(self, config: Mapping):
        self.config = config
    @classmethod
    def from_yaml(cls, yamlfile: os.PathLike):
        with open(yamlfile, 'r') as f:
            config=yaml.safe_load(f)
        return cls(config)

class Identifier:
    def identify(self, manager) -> str | None:
        pass

class RemoteServer: pass

class CameraManager: pass

class Logger: 
    def log_event(self, event, event_data):
        if event=='FrameDelay':
            return
        # print(event, event_data)

class Manager:
    frame_duration = 1/60
    DEFAULT_VARIABLES = {
        'default_reward_duration': 0.5,
    }
    def __init__(self,
                 data_directory: os.PathLike,
                 config: ConfigManager,
                 taskmanager: TaskManager,
                 renderer: Renderer,
                 eventmanager: EventManager,
                 datastore: DataStore | None = None,
                 iointerface: IOInterface | None = None,
                 cameramanager: CameraManager | None = None,
                 identifier: Identifier | None = None,
                 remoteserver: RemoteServer | None = None,
                 logger: Logger | None = None
                ):
        self.config = config
        self.strict_mode = config.get('strict_mode', False)
        self.variables = self.DEFAULT_VARIABLES.copy()
        self.variables.update(config.get('variables', {}))
        # set up our io devices
        if iointerface is None:
            io = config.pop('io', {})
            io_type = io.get('type', 'base')
            if io_type == 'base':
                iointerface = IOInterface()
        reward_params = io.pop('reward', None)
        if reward_params is not None:
            reward_device_type = reward_params.get('type')
            if reward_device_type == 'ISMATEC_SERIAL':
                address = reward_params.get("address")
                channel_info = reward_params.get('channels')
                from experiment.io.ismatec import IsmatecPumpSerial
                reward_device = IsmatecPumpSerial(address)
                reward_device.init(channel_info)

                iointerface.add_device('reward', reward_device)
            else:
                raise ValueError("Unsupported reward device type")
    
        self.renderer = renderer
        self.eventmanager = eventmanager
        self.iointerface = iointerface
        self.taskmanager = taskmanager
        self.identifier = identifier
        self.cameramanager = cameramanager
        self.remoteserver = remoteserver
        self.logger = logger
        self.session_directory = Path(data_directory, datetime.strftime(datetime.now(), "%Y%m%d_%H%M%S"))
        if not self.session_directory.exists():
            self.session_directory.mkdir(parents=True)
        if datastore is None:
            self.datastore = JSONDataStore(self.session_directory)
    
    def identify(self) -> str | None:
        """Identify the subject"""
        if self.identifier is None:
            return None
        identity = self.identifier.identify(self)
        return identity

    def good_monkey(self, **kwargs) -> None:
        """Reward the subject"""
        if (
            self.iointerface is None 
            or self.iointerface.devices.get('reward') is None):
            if self.strict_mode:
                raise ValueError("Cannot reward monkey if reward device is not provided")
            else:
                warnings.warn(
                    f"No reward device: Tried to reward monkey with params {kwargs}"
                )
                return
        self.iointerface.good_monkey(**kwargs)
    
    def run_trial(self, trial):
        """Run a trial"""
        continue_experiment = trial.run(self)
        self.datastore.flush()
        self.datastore.trialid += 1
        return continue_experiment

    def record(self, **kwargs):
        """Record data"""
        self.datastore.record(**kwargs)
    
    def cleanup(self):
        """Cleanup the experiment"""
        self.datastore.close()