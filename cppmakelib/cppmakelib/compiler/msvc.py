from cppmakelib.error.config      import ConfigError
from cppmakelib.error.subprocess  import SubprocessError
from cppmakelib.execution.run     import async_run
from cppmakelib.utility.decorator import syncable, unique
from cppmakelib.utility.version   import Version

class Msvc:
    name                = 'msvc'
    intermediate_suffix = '.i'
    preparsed_suffix    = '.pch'
    precompiled_suffix  = '.ixx'

    @syncable
    @unique
    async def __ainit__(self, path='cl'):
        self.path    = path
        self.version = await self._async_get_version()
        assert False
    
    async def _async_get_version(self):
        try:
            stdout = await async_run(command=[self.path], return_stdout=True)
            if 'msvc' in stdout.splitlines()[0].lower():
                version = Version.parse_from(stdout.splitlines()[0]).lower()
                if version >= 19:
                    return version
                else:
                    raise ConfigError(f'msvc is too old (with version = {version}, requires >= 19')
            else:
                raise ConfigError(f'msvc is not valid (with "{self.path} --version" returned "{stdout.replace('\n', ' ')}")')
        except SubprocessError as error:
            raise ConfigError(f'msvc is not valid (with "{self.path} --version" failed') from error
        except FileNotFoundError as error:
            raise ConfigError(f'msvc is not found (with "{self.path}" not found)') from error


        