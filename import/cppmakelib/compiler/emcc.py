from cppmakelib.compiler.clang import Clang

class Emcc(Clang):
    def        __init__(self, file: path = 'em++') -> None: ...
    async def __ainit__(self, file: path = 'em++') -> None: ...
    file               : path
    version            : Version
    compile_flags      : list[str]
    link_flags         : list[str]
    define_macros      : dict[str, str]
    stdlib_name        : str = 'libc++'
    stdlib_module_file : path
    stdlib_static_file : path
    stdlib_dynamic_file: path

    async def _async_get_version    (self) -> Version: ...
    async def _async_get_stdlib_name(self) -> str    : ...



from cppmakelib.basic.config       import config
from cppmakelib.error.config       import ConfigError
from cppmakelib.error.subprocess   import SubprocessError
from cppmakelib.executor.run       import async_run
from cppmakelib.utility.decorator  import member, syncable
from cppmakelib.utility.filesystem import path
from cppmakelib.utility.version    import Version

@member(Emcc)
@syncable
async def __ainit__(self: Emcc, file: path = 'em++') -> None:
    self.file               = file
    self.version            = await self._async_get_version()
    self.compile_flags = [
       f'-std={config.std}', '-fexceptions',
        *(['-O0', '-g'] if config.type == 'debug'   else
          ['-O3']       if config.type == 'release' else
          ['-Os']       if config.type == 'size'    else 
          [])
    ]
    self.link_flags = [
        *(['-s'] if config.type == 'release' or config.type == 'size' else []),
    ]
    self.define_macros = {
        **({'DEBUG' : 'true'} if config.type == 'debug'   else 
           {'NDEBUG': 'true'} if config.type == 'release' else 
           {})
    }
    self.stdlib_name        = 'libc++'
    self.stdlib_module_file = await self._async_get_stdlib_module_file()

@member(Emcc)
async def _async_get_version(self: Emcc) -> Version:
    try:
        stdout = await async_run(
            file=self.file,
            args=['--version'],
            return_stdout=True
        )
    except SubprocessError as error:
        raise ConfigError(f'emcc check failed (with file = {self.file})') from error
    try:
        version = Version.parse(pattern=r'^emcc \(.*\) (\d+)\.(\d+)\.(\d+)', string=stdout.splitlines()[0])
    except Version.ParseError as error:
        raise ConfigError(f'emcc check failed (with file = {self.file})') from error
    if version < 4:
        raise ConfigError(f'emcc version is too old (with file = {self.file}, version = {version}, requires = 4+)')
    return version

@member(Emcc)
async def _async_get_stdlib_module_file(self: Emcc) -> path:
    clang_stdlib_name = await Clang._async_get_stdlib_name(self)
    if clang_stdlib_name == 'libc++':
        try:
            return await Clang._async_get_stdlib_module_file(self)
        except ConfigError as error:
            raise ConfigError(f'libc++ module_file is not found (with file = {self.file})') from error
    else:
        raise ConfigError(f'libc++ module_file is not found (with file = {self.file}, clang_stdlib_name = {clang_stdlib_name})')
