from cppmakelib.basic.config        import config

from cppmakelib.builder.cmake       import cmake
from cppmakelib.builder.makefile    import makefile

from cppmakelib.compiler.all        import compiler
from cppmakelib.compiler.clang      import Clang
from cppmakelib.compiler.emcc       import Emcc
from cppmakelib.compiler.gcc        import Gcc

from cppmakelib.error.config        import ConfigError
from cppmakelib.error.logic         import LogicError
from cppmakelib.error.subprocess    import SubprocessError

from cppmakelib.executor.operation  import sync_wait, start_detached, when_all, when_any
from cppmakelib.executor.run        import async_run

from cppmakelib.system.all          import system
from cppmakelib.system.linux        import Linux
from cppmakelib.system.macos        import Macos
from cppmakelib.system.windows      import Windows

from cppmakelib.unit.executable     import Executable
from cppmakelib.unit.header         import Header
from cppmakelib.unit.module         import Module
from cppmakelib.unit.package        import Package
from cppmakelib.unit.source         import Source

self: Package
