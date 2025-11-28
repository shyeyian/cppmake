from cppmakelib.error.config   import ConfigError
from cppmakelib.system.linux   import Linux
from cppmakelib.system.macos   import Macos
from cppmakelib.system.windows import Windows

system = ...



suberrors = []
for System in (Linux, Macos, Windows):
    try:
        system = System()
        break
    except ConfigError as error:
        suberrors += [error]
else:
    raise ConfigError(f'system is not supported, because\n{'\n'.join([f" {error}" for error in suberrors])}')

def _set_system(new_system):
    global system
    system = new_system