from cppmakelib.error.logic        import LogicError
from cppmakelib.utility.filesystem import path
import importlib.util
import types
import typing

def import_module(file: path, globals: dict[str, typing.Any] = {}) -> types.ModuleType: ...



def import_module(file: path, globals: dict[str, typing.Any] = {}) -> types.ModuleType:
    try:
        spec = importlib.util.spec_from_file_location(name=file, location=file)
    except FileNotFoundError as error:
        raise LogicError(f'cppmake.py is not found (with file = {file})') from error
    if spec is None or spec.loader is None:
        raise LogicError(f'cppmake.py is not loaded (with file = {file})')
    module = importlib.util.module_from_spec(spec)
    module.__dict__.update(globals)
    spec.loader.exec_module(module)
    return module
