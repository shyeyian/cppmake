from cppmakelib.basic.config      import config
from cppmakelib.compiler.clang    import Clang
from cppmakelib.error.config      import ConfigError
from cppmakelib.error.subprocess  import SubprocessError
from cppmakelib.execution.run     import async_run
from cppmakelib.file.file_system  import Path, UnresolvedPath, resolve_path
from cppmakelib.utility.decorator import member, syncable, unique
from cppmakelib.utility.version   import Version

class Emcc(Clang):
    def           __init__    (self, file: Path | UnresolvedPath = UnresolvedPath('em++')) -> None: ...
    async def    __ainit__    (self, file: Path | UnresolvedPath = UnresolvedPath('em++')) -> None: ...
    name                = 'emcc'
    precompiled_suffix  = '.pcm'

    async def _async_get_version    (self) -> Version: ...
    async def _async_get_stdlib_name(self) -> str    : ...

@member(Emcc)
@syncable
@unique
async def __ainit__(
    self: Emcc, 
    file: Path | UnresolvedPath = UnresolvedPath('em++')
) -> None:
    self.file               = file if isinstance(file, Path) else resolve_path(file)
    self.version            = await self._async_get_version()
    self.stdlib_name        = 'libc++'
    self.stdlib_module_file = await self._async_get_stdlib_module_file()
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

@member(Emcc)
async def _async_get_version(self: Emcc) -> Version:
    try:
        stdout = await async_run(
            file=self.file,
            args=['--version'],
            return_stdout=True
        )
    except SubprocessError as error:
        raise ConfigError(f'emcc is not valid (with file = {self.file})') from error
    if not stdout.startswith('em++'):
        raise ConfigError(f'emcc is not valid (with file = {self.file}, subprocess = "{self.file} --version", stdout = "{stdout.splitlines()[0]} ...", requires = "em++ ...")')
    version = Version.parse(stdout)
    if version < 4:
        raise ConfigError(f'emcc is too old (with file = {self.file}, version = {version}, requires = 4+)')
    return version

@member(Emcc)
async def _async_get_stdlib_module_file(self: Emcc) -> Path:
    stdlib_name = await Clang._async_get_stdlib_name(self)
    if stdlib_name == 'libc++':
        try:
            return await Clang._async_get_stdlib_module_file(self)
        except ConfigError as error:
            raise ConfigError(f'libc++ module_file not found (with file = {self.file}, subcompiler = clang++)') from error
    else:
        raise ConfigError(f'libc++ module_file not found (with file = {self.file}, clang.stdlib_name = {stdlib_name})')
