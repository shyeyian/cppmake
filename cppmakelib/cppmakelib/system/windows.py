from cppmakelib.error.config      import ConfigError
from cppmakelib.file.file_system  import UnresolvedPath
from cppmakelib.utility.decorator import member
import sys

class Windows:
    def __init__(self) -> None: ...
    name             : str            = 'windows'
    executable_suffix: str            = '.exe'
    object_suffix    : str            = '.obj'
    static_suffix    : str            = '.lib'
    shared_suffix    : str            = '.dll'
    compiler         : UnresolvedPath = UnresolvedPath('cl.exe')
    linker           : UnresolvedPath = UnresolvedPath('link.exe')

    def _check(self) -> None: ...



@member(Windows)
def __init__(self: Windows) -> None:
    self._check()

@member(Windows)
def _check(self: Windows) -> None:
    if sys.platform != 'win32' and sys.platform != 'win64':
        raise ConfigError(f'windows check failed (with sys.platform = {sys.platform})')