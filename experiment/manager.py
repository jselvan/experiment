import yaml
from collections.abc import Mapping
import os
from experiment.renderers.base import Renderer

class ConfigManager: 
    def __init__(self, config: Mapping):
        self.config = config
    @classmethod
    def from_yaml(cls, yamlfile: os.PathLike):
        with open(yamlfile, 'r') as f:
            config=yaml.safe_load(f)
        return cls(config)
class TaskManager: pass
class EventManager: pass
class IOInterface: pass
class Identifier:
    def identify(self, manager) -> str | None:
        pass
class RemoteServer: pass
class CameraManager: pass
class Logger: pass

class Manager:
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


