from .basic.config     import config

from .builder.cmake    import cmake
from .builder.git      import git
from .builder.include  import include
from .builder.makefile import makefile

from .compiler.all     import compiler
from .compiler.clang   import Clang
from .compiler.emcc    import Emcc
from .compiler.gcc     import Gcc
from .compiler.msvc    import Msvc

from .error.config     import ConfigError
from .error.logic      import LogicError
from .error.subprocess import SubprocessError

from .file.file_system import *

from .execution.run    import run

from .system.all       import system
from .system.linux     import Linux
from .system.macos     import Macos
from .system.windows   import Windows

from .unit.executable  import Executable
from .unit.module      import Module
from .unit.package     import Package
from .unit.source      import Source

global self