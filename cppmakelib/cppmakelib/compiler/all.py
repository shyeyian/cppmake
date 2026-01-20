from cppmakelib.basic.config   import config
from cppmakelib.compiler.clang import Clang
from cppmakelib.compiler.emcc  import Emcc
from cppmakelib.compiler.gcc   import Gcc
from cppmakelib.error.config   import ConfigError

def _choose_compiler() -> Clang | Emcc | Gcc:
    matches: list[Clang | Emcc | Gcc] = []
    errors : list[Exception]          = []
    for Compiler in (Clang, Emcc, Gcc):
        try:
            matches += [Compiler(config.compiler)]
        except ConfigError as error:
            errors += [error]
    if len(matches) == 0:
        raise ConfigError(f'compiler "{config.compiler} is not supported (with matches = {matches})') \
            from ExceptionGroup('no compiler is matched', errors)
    elif len(matches) == 1:
        return matches[0]
    else:
        raise ConfigError(f'compiler "{config.compiler} is ambiguous (with matches = {matches})')

compiler = _choose_compiler()