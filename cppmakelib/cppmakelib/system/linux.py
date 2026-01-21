from cppmakelib.error.config      import ConfigError
from cppmakelib.file.file_system  import UnresolvedPath
from cppmakelib.utility.decorator import member
import sys

class Linux:
    def __init__(self) -> None: ...
    name             : str            = 'linux'
    executable_suffix: str            = ''
    object_suffix    : str            = '.o'
    static_suffix    : str            = '.a'
    shared_suffix    : str            = '.so'
    compiler         : UnresolvedPath = UnresolvedPath('g++')
    linker           : UnresolvedPath = UnresolvedPath('lld')

    def _check(self) -> None: ...



@member(Linux)
def __init__(self: Linux) -> None:
    self._check()

@member(Linux)
def _check(self: Linux) -> None:
    if sys.platform != 'linux':
        raise ConfigError(f'linux check failed (with sys.platform = {sys.platform})')