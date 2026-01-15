from cppmakelib.error.config      import ConfigError
from cppmakelib.utility.decorator import member
import sys

class Linux:
    name              = 'linux'
    executable_suffix = ''
    static_suffix     = '.a'
    shared_suffix     = '.so'
    compiler_path     = 'g++'
    linker_path       = 'lld'
    def __init__(self): ...



@member(Linux)
def __init__(self):
    self._check()

@member(Linux)
def _check(self):
    if sys.platform != 'linux':
        raise ConfigError(f'system is not linux (with sys.platform = {sys.platform})')