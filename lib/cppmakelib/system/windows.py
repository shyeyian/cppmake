class Windows:
    def __init__(self) -> None: ...
    executable_suffix: str  = '.exe'
    object_suffix    : str  = '.obj'
    static_suffix    : str  = '.lib'
    dynamic_suffix   : str  = '.dll'
    compiler         : path = 'cl.exe'

    def _check(self) -> None: ...



from cppmakelib.error.config       import ConfigError
from cppmakelib.utility.decorator  import member
from cppmakelib.utility.filesystem import path
import sys

@member(Windows)
def __init__(self: Windows) -> None:
    self._check()

@member(Windows)
def _check(self: Windows) -> None:
    if sys.platform != 'win32' and sys.platform != 'win64':
        raise ConfigError(f'windows check failed (with sys.platform = {sys.platform})')