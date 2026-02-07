class Macos:
    def __init__(self) -> None: ...
    executable_suffix: str  = ''
    object_suffix    : str  = '.o'
    static_suffix    : str  = '.a'
    dynamic_suffix   : str  = '.dylib'
    compiler         : path = 'clang++'

    def _check(self) -> None: ...



from cppmakelib.error.config       import ConfigError
from cppmakelib.utility.decorator  import member
from cppmakelib.utility.filesystem import path
import sys

@member(Macos)
def __init__(self: Macos) -> None:
    self._check()

@member(Macos)
def _check(self: Macos) -> None:
    if sys.platform != 'darwin':
        raise ConfigError(f'macos check failed (with sys.platform = {sys.platform})')