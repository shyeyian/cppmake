from cppmakelib.error.config      import ConfigError
from cppmakelib.utility.decorator import member
import sys

class Macos:
    name              = 'macos'
    executable_suffix = ''
    static_suffix     = '.a'
    shared_suffix     = '.dylib'
    compiler_path     = 'clang++'
    linker_path       = 'ld'
    def __init__(self): ...



@member(Macos)
def __init__(self):
    self._check()

@member(Macos)
def _check(self):
    if sys.platform != 'darwin':
        raise ConfigError(f'system is not macos (with sys.platform = {sys.platform})')