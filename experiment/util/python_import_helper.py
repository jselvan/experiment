import importlib.util

def load_module(path):
    spec = importlib.util.spec_from_file_location("module", path)
    assert spec is not None and spec.loader is not None, "Could not load module from path: {}".format(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_object_from_module(path, object_name):
    module = load_module(path)
    return getattr(module, object_name)