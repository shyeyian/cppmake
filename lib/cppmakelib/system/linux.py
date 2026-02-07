class Linux:
    def __init__(self) -> None: ...
    executable_suffix: str  = ''
    object_suffix    : str  = '.o'
    static_suffix    : str  = '.a'
    dynamic_suffix   : str  = '.so'
    compiler         : path = 'g++'

    def _check(self) -> None: ...



from cppmakelib.error.config       import ConfigError
from cppmakelib.utility.decorator  import member
from cppmakelib.utility.filesystem import path
import sys

@member(Linux)
def __init__(self: Linux) -> None:
    self._check()

@member(Linux)
def _check(self: Linux) -> None:
    if sys.platform != 'linux':
        raise ConfigError(f'linux check failed (with sys.platform = {sys.platform})')