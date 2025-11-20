from cppmake.error.config      import ConfigError
from cppmake.utility.decorator import member
import os
import sys

class Windows:
    name              = "windows"
    executable_suffix = ".exe"
    static_suffix     = ".lib"
    shared_suffix     = ".dll"
    compiler_path     = "cl.exe"
    env               = os.environ
    def __init__(self): ...



@member(Windows)
def __init__(self):
    Windows._check()

@member(Windows)
def _check():
    if sys.platform != "darwin":
        raise ConfigError(f"system is not windows (with sys.platform = {sys.platform})")