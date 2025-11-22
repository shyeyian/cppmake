from cppmakelib.basic.config import config
from cppmakelib.error.config import ConfigError
import importlib

def import_file(file, globals={}): ...



_counter = 0
def import_file(file, globals={}):
    global _counter
    try:
        module = importlib.util.module_from_spec(importlib.util.spec_from_file_location(file, file))
        module.__dict__.update(globals
                               )

        module = importlib.machinery.SourceFileLoader(
            fullname=file.removesuffix(".py").replace('/', '.'), 
            path=file
        ).load_module()
    except FileNotFoundError:
        raise ConfigError(f"cppmake.py is not found (with path = {file})")
    return module
