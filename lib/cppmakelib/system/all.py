from cppmakelib.error.config   import ConfigError
from cppmakelib.system.linux   import Linux
from cppmakelib.system.macos   import Macos
from cppmakelib.system.windows import Windows

system: Linux | Macos | Windows



def _choose_system() -> Linux | Macos | Windows:
    matches: list[Linux | Macos | Windows] = []
    errors : list[Exception]               = []
    for System in (Linux, Macos, Windows):
        try:
            matches += [System()]
        except ConfigError as error:
            errors += [error]
    if len(matches) == 0:
        raise ConfigError(f'system is not recognized') from ExceptionGroup('no system is matched', errors)
    elif len(matches) == 1:
        return matches[0]
    else:
        raise ConfigError(f'system is ambiguous (with matches = {matches})')

system = _choose_system()