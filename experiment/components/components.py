from experiment.manager import Manager
from experiment.components.messages import MessageType

from typing import Any, Optional

class BaseComponent:
    COMPONENT_TYPE = "base"
    SINGLETON = True

    def __init__(self):
        self.manager = None
        self.message_handlers = {}

    def register(self, mgr: Manager):
        self.manager = mgr
        self.manager.register_component(self)

    def notify(self, message_type: MessageType, message: Any):
        if self.manager:
            self.manager.notify(message_type, message, announcer=self)

    def listen(self, message_type: MessageType, message: Any, announcer: "BaseComponent | Manager"):
        handler = self.message_handlers.get(message_type)
        if handler is not None:
            handler(message, announcer)