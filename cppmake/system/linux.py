from cppmake.error.config      import ConfigError
from cppmake.utility.decorator import member
import os
import sys

class Linux:
    name              = "linux"
    executable_suffix = ""
    static_suffix     = ".a"
    shared_suffix     = ".so"
    compiler_path     = "g++"
    env               = os.environ
    def __init__(self): ...



@member(Linux)
def __init__(self):
    Linux._check()

@member(Linux)
def _check():
    if sys.platform != "linux":
        raise ConfigError(f"system is not linux (with sys.platform = {sys.platform})")