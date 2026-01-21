from cppmakelib.basic.config      import config
from cppmakelib.compiler.clang    import Clang
from cppmakelib.error.config      import ConfigError
from cppmakelib.error.subprocess  import SubprocessError
from cppmakelib.execution.run     import async_run
from cppmakelib.file.file_system  import Path, UnresolvedPath
from cppmakelib.utility.decorator import member, syncable, unique
from cppmakelib.utility.version   import Version

class Emcc(Clang):
    def        __init__(self, file: Path | UnresolvedPath = UnresolvedPath('em++')) -> None: ...
    async def __ainit__(self, file: Path | UnresolvedPath = UnresolvedPath('em++')) -> None: ...
    name              : str = 'emcc'
    file              : Path
    version           : Version
    stdlib_name       : str = 'libc++'
    stdlib_module_file: Path
    stdlib_static_file: Path
    stdlib_shared_file: Path
    compile_flags     : list[str]
    link_flags        : list[str]
    define_macros     : dict[str, str]

    async def _async_get_version    (self) -> Version: ...
    async def _async_get_stdlib_name(self) -> str    : ...

@member(Emcc)
@syncable
@unique
async def __ainit__(
    self: Emcc, 
    file: Path | UnresolvedPath = UnresolvedPath('em++')
) -> None:
    self.file               = file if isinstance(file, Path) else file.resolved_path()
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
        raise ConfigError(f'emcc check failed (with file = {self.file})') from error
    if not stdout.startswith('em++'):
        raise ConfigError(f'emcc check failed (with file = {self.file}, subprocess = "{self.file} --version", stdout = "{stdout.splitlines()[0]} ...", requires = "em++ ...")')
    version = Version.parse(stdout)
    if version < 4:
        raise ConfigError(f'emcc version is too old (with file = {self.file}, version = {version}, requires = 4+)')
    return version

@member(Emcc)
async def _async_get_stdlib_module_file(self: Emcc) -> Path:
    clang_stdlib_name = await Clang._async_get_stdlib_name(self)
    if clang_stdlib_name == 'libc++':
        try:
            return await Clang._async_get_stdlib_module_file(self)
        except ConfigError as error:
            raise ConfigError(f'libc++ module_file is not found (with file = {self.file}, subcompiler = clang++)') from error
    else:
        raise ConfigError(f'libc++ module_file is not found (with file = {self.file}, clang_stdlib_name = {clang_stdlib_name})')
