import time
import warnings
from typing import Mapping, Optional, Callable, Any, Optional, List, Dict
from typing import TYPE_CHECKING
from pathlib import Path
if TYPE_CHECKING:
    from experiment.components.components import BaseComponent, MessageType
    from experiment.components.io.base import IOInterface
    from experiment.components.remote.base import RemoteServer
    from experiment.components.renderer.base import Renderer
    from experiment.components.events.base import EventManager

from experiment.components.identifier import Identifier

class Manager:
    frame_duration = 1/60
    DEFAULT_VARIABLES = {
        'default_reward_duration': 0.5,
        'strict_mode': True,
    }
    DEFAULT_DATA_DIRECTORY = "~/experiment/data"
    def __init__(self, 
        variables: Optional[Dict[str, Any]] = None,
        data_directory: Optional[str] = None
    ):
        self.components: List["BaseComponent"] = []
        self.variables: Dict[str, Any] = self.DEFAULT_VARIABLES.copy()
        self.strict_mode: bool = self.variables.pop('strict_mode', True)
        if variables:
            self.variables.update(variables)
        
        # Set up data directory
        if data_directory is None:
            data_directory = self.DEFAULT_DATA_DIRECTORY
        self.data_directory = Path(data_directory).expanduser()
        if not self.data_directory.exists():
            self.data_directory.mkdir(parents=True, exist_ok=True)
        self.session_directory: Optional[Path] = None

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "Manager":
        variables = config.pop('variables', None)  # Currently not used
        manager = cls(variables=variables)
        for component_config in config.get('components', []):
            from experiment.components.from_config import initialize_component_from_config
            component = initialize_component_from_config(component_config)
            component.register(manager)
        return manager
    
    def initialize(self):
        """Initialize all components"""
        for component in self.components:
            component.initialize()

    def start_session(self):
        """Start a new session by creating a session directory"""
        self.session_directory = self.data_directory / time.strftime("%Y%m%d_%H%M%S")
        self.session_directory.mkdir(parents=True, exist_ok=True)
        return self.session_directory

    def get_session_directory(self) -> Path:
        """Get or create the session directory"""
        if self.session_directory is None:
            self.start_session()
        assert self.session_directory is not None, "Session directory could not be created"
        return self.session_directory

    def register_component(self, component: "BaseComponent"):
        """Register a component with the manager"""
        component_type = component.COMPONENT_TYPE
        for comp in self.components:
            if comp.COMPONENT_TYPE == component_type and comp.SINGLETON:
                raise ValueError(f"Component of type {component_type} is already registered as singleton")
        self.components.append(component)

    def unregister_component(self, component: "BaseComponent"):
        """Unregister a component from the manager"""
        if component in self.components:
            self.components.remove(component)
        else:
            raise ValueError("Component is not registered")

    def unregister_component_by_type(self, component_type: str):
        """Unregister a component from the manager by its type"""
        for component in self.components:
            if component.COMPONENT_TYPE == component_type:
                self.components.remove(component)

    def unregister_all_components(self):
        """Unregister all components from the manager"""
        self.components.clear()

    def notify(self, message_type: "MessageType", message: Any, announcer: "Optional[BaseComponent | Manager]" = None):
        """Notify all components of a message"""
        if announcer is None:
            announcer = self
        for component in self.components:
            if component is not announcer:
                component.listen(message_type, message, announcer)

    @property
    def identifier(self) -> Optional[Identifier]:
        for component in self.components:
            if component.COMPONENT_TYPE == 'identifier':
                return component #type: ignore
    
    @property
    def iointerface(self) -> Optional["IOInterface"]:
        for component in self.components:
            if component.COMPONENT_TYPE == 'io_interface':
                return component #type: ignore
        return None

    @property
    def datastore(self) -> Any:
        for component in self.components:
            if component.COMPONENT_TYPE == 'datastore':
                return component #type: ignore
        raise ValueError("No datastore component registered")

    @property
    def logger(self) -> Any:
        for component in self.components:
            if component.COMPONENT_TYPE == 'logger':
                return component #type: ignore
        raise ValueError("No logger component registered")

    def log(self, level: str, message: str):
        """Log a message using the logger component"""
        self.logger.log(level, message)

    @property
    def remoteserver(self) -> "Optional[RemoteServer]":
        for component in self.components:
            if component.COMPONENT_TYPE == 'remoteserver':
                return component #type: ignore
        return None

    @property
    def renderer(self) -> "Optional[Renderer]":
        for component in self.components:
            if component.COMPONENT_TYPE == 'renderer':
                return component #type: ignore
        return None

    @property
    def eventmanager(self) -> "Optional[EventManager]":
        for component in self.components:
            if component.COMPONENT_TYPE == 'eventmanager':
                return component #type: ignore
        return None

    def identify(self) -> str | None:
        """Identify the subject"""
        if self.identifier is None:
            return None
        identity = self.identifier.identify(self)
        return identity

    def good_monkey(self, **kwargs) -> Optional[Mapping[str, Callable[[], None]]]:
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
    
    def run_trial(self, trial):
        """Run a trial"""
        continue_experiment = trial.run(self)
        self.datastore.flush()
        self.datastore.trialid += 1
        if self.remoteserver is not None:
            self.remoteserver.notify_trial_end()
        return continue_experiment

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