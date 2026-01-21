from cppmakelib.error.config      import ConfigError
from cppmakelib.file.file_system  import UnresolvedPath
from cppmakelib.utility.decorator import member
import sys

class Macos:
    def __init__(self) -> None: ...
    name             : str            = 'macos'
    executable_suffix: str            = ''
    object_suffix    : str            = '.o'
    static_suffix    : str            = '.a'
    shared_suffix    : str            = '.dylib'
    compiler         : UnresolvedPath = UnresolvedPath('clang++')
    linker           : UnresolvedPath = UnresolvedPath('ld')

    def _check(self) -> None: ...



@member(Macos)
def __init__(self: Macos) -> None:
    self._check()

@member(Macos)
def _check(self: Macos) -> None:
    if sys.platform != 'darwin':
        raise ConfigError(f'macos check failed (with sys.platform = {sys.platform})')