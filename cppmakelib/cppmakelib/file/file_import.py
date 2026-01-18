from cppmakelib.error.config     import ConfigError
from cppmakelib.file.file_system import Path
import importlib.util

def import_file(file: Path, globals: dict[str, str] = {}): ...



def import_file(file: Path, globals: dict[str, str] = {}):
    try:
        spec = importlib.util.spec_from_file_location(name=file.__str__(), location=file._handle)
    except FileNotFoundError as error:
        raise ConfigError(f'cppmake.py is not found') from error
    if spec is None or spec.loader is None:
        raise ConfigError(f'cppmake.py is not loaded (with file = {file})')
    module = importlib.util.module_from_spec(spec)
    module.__dict__.update(globals)
    spec.loader.exec_module(module)
    return module
