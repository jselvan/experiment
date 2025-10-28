import importlib

def initialize_component_from_config(config):
    # Get the import path and class name
    module_path = config.pop("module", None)
    class_name = config.pop("class", None)
    if not module_path or not class_name:
        raise ValueError("Component config must have 'module' and 'class' fields")
    # Import the module and get the class
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(**config)