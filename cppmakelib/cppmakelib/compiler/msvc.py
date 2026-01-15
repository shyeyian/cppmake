from cppmakelib.error.config      import ConfigError
from cppmakelib.error.subprocess  import SubprocessError
from cppmakelib.execution.run     import async_run
from cppmakelib.utility.decorator import syncable, unique
from cppmakelib.utility.version   import Version
import sys

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
        return Version.async_parse(
            name   =self.name,
            command=[self.path],
            pipe   =sys.stderr,
            check  =lambda stderr: stderr.startswith('Microsoft') and 'msvc' in stderr,
            lowest =19.36
        )