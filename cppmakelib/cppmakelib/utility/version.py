from cppmakelib.error.config      import ConfigError
from cppmakelib.error.logic       import LogicError
from cppmakelib.error.subprocess  import SubprocessError
from cppmakelib.execution.run     import async_run
from cppmakelib.utility.decorator import syncable
import functools
import re
import sys

@functools.total_ordering
class Version:
    def __init__(self, major, minor=0, patch=0):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'
    
    def __eq__(self, other):
        if type(other) is Version:
            return self.major == other.major and self.minor == other.minor and self.patch == other.patch
        else:
            return NotImplemented
        
    def __lt__(self, other):
        if type(other) is Version:
            return (self.major <  other.major) or \
                   (self.major == other.major and self.minor <  other.minor) or \
                   (self.major == other.major and self.minor == other.minor and self.patch < other.patch)
        elif type(other) is int:
            return self < Version(other)
        elif type(other) is float:
            numbers = str(other).split('.')
            return self < Version(numbers[0], *([numbers[1]] if len(numbers) >= 2 else []))
        else:
            return NotImplemented
        
    @syncable
    async def async_parse(name, command, check, pipe=sys.stdout, lowest=0):
        try:
            output = await async_run(command=command, return_stdout=(pipe is sys.stdout), return_stderr=(pipe is sys.stderr))
            if check(output):
                word = re.search(r'\b\d+(\.\d+)+\b', output)
                if word is None:
                    raise LogicError(f'version parse failed (with output = {output})')
                version = Version(*[int(split) for split in word.group().split('.')[:3]])
                if version >= lowest:
                    return version
                else:
                    raise ConfigError(f'{name} is too old (with version = {version}, requires >= {lowest})')
            else:
                raise ConfigError(f'{name} is not valid (with "{' '.join(command)}" returned "{output.replace('\n', ' ')}")')
        except SubprocessError as error:
            raise ConfigError(f'{name} is not valid (with "{' '.join(command)}" failed)') from error
        except FileNotFoundError as error:
            raise ConfigError(f'{name} is not found (with "{' '.join(command)}" not found)') from error