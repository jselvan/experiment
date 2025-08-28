from collections.abc import Mapping, Sequence
import os
from pathlib import Path
from datetime import datetime

import json
import warnings
warnings.simplefilter("always")
import time

from experiment.components.renderers import Renderer
from experiment.taskmanager import TaskManager
from experiment.components.events import EventManager, Event
from experiment.components.datastore import DataStore
from experiment.components.io import IOInterface

from typing import TYPE_CHECKING, Any, Optional, List, Dict
if TYPE_CHECKING:
    from experiment.components import BaseComponent, MessageType

class Manager:
    frame_duration = 1/60
    DEFAULT_VARIABLES = {
        'default_reward_duration': 0.5,
    }
    def __init__(self, components: Optional[List[BaseComponent]] = None, strict_mode: bool = True):
        self.components: List[BaseComponent] = []
        if components is not None:
            for component in components:
                self.register_component(component)
        self.strict_mode = strict_mode
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "Manager":
        strict_mode = config.pop("strict_mode", True)
        components = []
        for comp_config in config.get("components", []):
            component = initialize_component_from_config(comp_config)
            components.append(component)
        return cls(components=components, strict_mode=strict_mode)

    @classmethod
    def from_toml(cls, config_path: str | Path) -> "Manager":
        import tomllib
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
        return cls.from_config(config)

    @property
    def iointerface(self) -> IOInterface | None:
        for component in self.components:
            if component.COMPONENT_TYPE == 'io_interface':
                return component #type: ignore
        return None
    
    @property
    def identifier(self) -> Optional[BaseComponent]:
        for component in self.components:
            if component.COMPONENT_TYPE == 'identifier':
                return component #type: ignore
    
    @property
    def datastore(self) -> DataStore | None:
        for component in self.components:
            if component.COMPONENT_TYPE == 'datastore':
                return component #type: ignore
        return None

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
        if self.datastore is None:
            if self.strict_mode:
                raise ValueError("Cannot run trial without a datastore")
            else:
                warnings.warn("No datastore: Trial data will not be recorded")
        continue_experiment = trial.run(self)
        data = {"trial": trial, "continue_experiment": continue_experiment}
        if not self.datastore is None:
            self.datastore.flush()
            data.update(**self.datastore.current_trial_record)
            self.datastore.trialid += 1
        return data

    def record(self, **kwargs):
        """Record data"""
        if self.datastore is None:
            if self.strict_mode:
                raise ValueError("Cannot record data without a datastore")
            else:
                warnings.warn("No datastore: Trial data will not be recorded")
        else:
            self.datastore.record(**kwargs)
    
    def cleanup(self):
        """Cleanup the experiment"""
        if self.datastore is not None:
            self.datastore.close()
        if self.remoteserver is not None:
            self.remoteserver.stop()
    
    def get_time(self) -> float:
        """Get the current time"""
        return time.time()

    def register_component(self, component: BaseComponent):
        """Register a component with the manager"""
        if component.COMPONENT_TYPE is None or component.COMPONENT_TYPE == 'base':
            raise ValueError("Component must have a component type defined that is not base or None")
        if component.SINGLETON:
            for existing in self.components:
                if existing.COMPONENT_TYPE == component.COMPONENT_TYPE:
                    raise ValueError(f"Component of type {component.COMPONENT_TYPE} is a singleton and has already been registered")
        self.components.append(component)

    def unregister_component(self, component: BaseComponent):
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

    def notify(self, message_type: MessageType, message: Any, announcer: "Optional[BaseComponent|Manager]" = None):
        if announcer is None:
            announcer = self
        for component in self.components:
            if component is announcer:
                continue
            component.listen(message_type, message, announcer=announcer)