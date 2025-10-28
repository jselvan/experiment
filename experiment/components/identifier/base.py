from experiment.components.components import BaseComponent

class Identifier(BaseComponent):
    COMPONENT_TYPE = "identifier"
    def identify(self, data):
        raise NotImplementedError("Subclasses must implement this method.")