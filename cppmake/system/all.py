from cppmake.error.config   import ConfigError
from cppmake.system.linux   import Linux
from cppmake.system.macos   import Macos
from cppmake.system.windows import Windows

system = ...



suberrors = []
for System in (Linux, Macos, Windows):
    try:
        system = System()
        break
    except ConfigError as error:
        suberrors += [error]
else:
    raise ConfigError(
        f'system is not supported, because\n'
        ''.join([f'  {error}\n' for error in suberrors])
    )
