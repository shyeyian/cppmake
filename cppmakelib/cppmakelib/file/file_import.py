from cppmakelib.basic.config import config
from cppmakelib.error.config import ConfigError
import importlib.util

def import_file(file, globals={}): ...



_counter = 0
def import_file(file, globals={}):
    global _counter
    try:
        spec   = importlib.util.spec_from_file_location(file, file)
        module = importlib.util.module_from_spec(spec)
        module.__dict__.update(globals)
        spec.loader.exec_module(module)
        return module
    except FileNotFoundError:
        raise ConfigError(f"cppmake.py is not found (with path = {file})")
