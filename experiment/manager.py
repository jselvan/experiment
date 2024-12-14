from collections.abc import Mapping, Sequence
import os

import yaml

from experiment.renderers.base import Renderer
from experiment.taskmanager import TaskManager
from experiment.events import EventManager, Event

class ConfigManager: 
    def __init__(self, config: Mapping):
        self.config = config
    @classmethod
    def from_yaml(cls, yamlfile: os.PathLike):
        with open(yamlfile, 'r') as f:
            config=yaml.safe_load(f)
        return cls(config)

class DataStore:
    pass

class IOInterface:
    def good_monkey(self, **kwargs):
        pass

class Identifier:
    def identify(self, manager) -> str | None:
        pass

class RemoteServer: pass

class CameraManager: pass

class Logger: 
    def log_event(self, event, event_data):
        print(event, event_data)

class Manager:
    frame_duration = 1/60
    def __init__(self,
                 config: ConfigManager,
                 taskmanager: TaskManager,
                 renderer: Renderer,
                 eventmanager: EventManager,
                 iointerface: IOInterface | None = None,
                 cameramanager: CameraManager | None = None,
                 identifier: Identifier | None = None,
                 remoteserver: RemoteServer | None = None,
                 logger: Logger | None = None
                ):
        self.config = config
        self.renderer = renderer
        self.eventmanager = eventmanager
        self.iointerface = iointerface
        self.taskmanager = taskmanager
        self.identifier = identifier
        self.cameramanager = cameramanager
        self.remoteserver = remoteserver
        self.logger = logger
    
    def identify(self) -> str | None:
        """Identify the subject"""
        if self.identifier is None:
            return None
        identity = self.identifier.identify(self)
        return identity

    def good_monkey(self, **kwargs) -> None:
        """Reward the subject"""
        if self.iointerface is None:
            raise ValueError("Cannot reward monkey if io interface is not provided")
        self.iointerface.good_monkey(**kwargs)
