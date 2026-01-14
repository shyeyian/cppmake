from cppmakelib.basic.config   import config
from cppmakelib.compiler.clang import Clang
from cppmakelib.compiler.emcc  import Emcc
from cppmakelib.compiler.gcc   import Gcc
from cppmakelib.compiler.msvc  import Msvc
from cppmakelib.error.config   import ConfigError

def _choose_compiler():
    suberrors = []
    for Compiler in (Clang, Emcc, Gcc, Msvc):
        try:
            return Compiler(config.compiler)
        except ConfigError as error:
            suberrors += [error]
    else:
        raise ConfigError(f'compiler "{config.compiler}" is not supported') from ExceptionGroup('no compiler is available', suberrors)

compiler = _choose_compiler()