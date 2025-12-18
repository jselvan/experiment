from typing import Mapping, Dict, TYPE_CHECKING, Callable, Any
import os
from pathlib import Path
from datetime import datetime

import yaml
import json
import warnings
warnings.simplefilter("always")
import time

from experiment.renderers.base import Renderer
from experiment.taskmanager import TaskManager
from experiment.events import EventManager, Event
from experiment.datastore.base import DataStore
from experiment.datastore.jsonstore import JSONDataStore
from experiment.io.base import IOInterface

if TYPE_CHECKING:
    from experiment.remote.base import RemoteServer
    from experiment.trial import Trial, TrialResult

class Identifier:
    def identify(self, manager) -> str | None:
        pass

class CameraManager: pass

class Logger: 
    def __init__(self):
        self.streams = []
    def register_stream_handler(self, stream):
        self.streams.append(stream)
    def log_event(self, event, event_data):
        for stream in self.streams:
            if event == 'FrameDelay':
                continue
            with open(stream, 'a') as f:
                f.write(json.dumps(event_data))
                f.write('\n')
    def close(self):
        for stream in self.streams:
            # stream.close()
            pass

class Manager:
    frame_duration = 1/60
    DEFAULT_VARIABLES = {
        'default_reward_duration': 0.5,
    }
    def __init__(self,
                 data_directory: os.PathLike,
                 config: Dict[str, Any],
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
            else:
                raise ValueError("Unsupported IO interface type")

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
    
        remote_settings = config.get('remote_server', {})
        remote_enabled = remote_settings.get('enabled', False) or config.get('remote', False)
        if remoteserver is None and remote_enabled:
            from experiment.remote.flask import FlaskServer
            print("Starting remote server...")
            print(f"Remote server settings: {remote_settings}")
            remoteserver = FlaskServer(self, 
                show=remote_settings.get('show', True), 
                template_path=remote_settings.get('template_path', None)
            )
            remoteserver.start()

        self.renderer = renderer
        self.eventmanager = eventmanager
        self.iointerface = iointerface
        self.taskmanager = taskmanager
        self.identifier = identifier
        self.cameramanager = cameramanager
        self.remoteserver = remoteserver
        if logger is None:
            logger = Logger()
        self.logger = logger
        self.session_directory = Path(data_directory, datetime.strftime(datetime.now(), "%Y%m%d_%H%M%S"))
        if not self.session_directory.exists():
            self.session_directory.mkdir(parents=True)
        if datastore is None:
            self.datastore = JSONDataStore(self.session_directory)
        else:
            self.datastore = datastore
            datastore.session_directory = self.session_directory
        self.logger.register_stream_handler(
            self.session_directory/'manager.log'
        )
    
    def identify(self) -> str | None:
        """Identify the subject"""
        if self.identifier is None:
            return None
        identity = self.identifier.identify(self)
        return identity

    def good_monkey(self, **kwargs) -> None | Dict[str, Callable]:
        """Reward the subject"""
        if (
            self.iointerface is None 
            or self.iointerface.devices.get('reward') is None):
            if self.strict_mode:
                raise ValueError("Cannot reward monkey if reward device is not provided")
            elif kwargs.get('return_callbacks', False):
                warnings.warn(
                    f"No reward device: Tried to reward monkey with params {kwargs}"
                )
                return {
                    'reward_setup_callback': lambda: print("No reward device setup"),
                    'reward_on_callback': lambda: print("No reward device on"),
                    'reward_off_callback': lambda: print("No reward device off"),
                }
            else:
                warnings.warn(
                    f"No reward device: Tried to reward monkey with params {kwargs}"
                )
                return
        return self.iointerface.good_monkey(**kwargs)
    
    def run_session(self, blockmanager) -> None:
        continue_session = True
        while continue_session:
            trial = blockmanager.get_next_trial()
            result = self.run_trial(trial)
            continue_session = result.continue_session
            blockmanager.parse_results(result)

    def run_trial(self, trial: Trial) -> TrialResult:
        """Run a trial"""
        result = trial.run(self)
        self.datastore.flush()
        self.datastore.trialid += 1
        if self.remoteserver is not None:
            self.remoteserver.notify_trial_end()
        return result

    def record(self, **kwargs):
        """Record data"""
        self.datastore.record(**kwargs)
    
    def cleanup(self):
        """Cleanup the experiment"""
        self.datastore.close()
        self.logger.close()
        if self.remoteserver is not None:
            self.remoteserver.stop()
    
    def get_time(self) -> float:
        """Get the current time"""
        return time.time()