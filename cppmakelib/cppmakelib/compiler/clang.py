from cppmakelib.basic.config      import config
from cppmakelib.compiler.gcc      import Gcc
from cppmakelib.error.config      import ConfigError
from cppmakelib.error.subprocess  import SubprocessError
from cppmakelib.execution.run     import async_run
from cppmakelib.file.file_system  import Path, UnresolvedPath, create_dir, exist_file
from cppmakelib.utility.decorator import member, syncable, unique
from cppmakelib.utility.version   import Version

class Clang(Gcc):
    def           __init__    (self, file: Path | UnresolvedPath = UnresolvedPath('clang++'))                                                                                                                                                                         -> None: ...
    async def    __ainit__    (self, file: Path | UnresolvedPath = UnresolvedPath('clang++'))                                                                                                                                                                         -> None: ...
    def             precompile(self, module_file: Path, interface_file: Path, object_file: Path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [], import_dirs: list[Path] = [], diagnostic_file: Path | None = None) -> None: ...
    async def async_precompile(self, module_file: Path, interface_file: Path, object_file: Path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [], import_dirs: list[Path] = [], diagnostic_file: Path | None = None) -> None: ...
    def             compile   (self, source_file: Path,                       object_file: Path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [], import_dirs: list[Path] = [], diagnostic_file: Path | None = None) -> None: ...
    async def async_compile   (self, source_file: Path,                       object_file: Path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [], import_dirs: list[Path] = [], diagnostic_file: Path | None = None) -> None: ...
    name              : str = 'clang'
    precompiled_suffix: str = '.pcm'
    file              : Path
    version           : Version
    stdlib_name       : str
    stdlib_module_file: Path
    stdlib_static_file: Path
    stdlib_shared_file: Path
    compile_flags     : list[str]
    link_flags        : list[str]
    define_macros     : dict[str, str]

    async def _async_get_version           (self) -> Version: ...
    async def _async_get_stdlib_name       (self) -> str: ...
    async def _async_get_stdlib_module_file(self) -> Path   : ...



@member(Clang)
@syncable
@unique
async def __ainit__(
    self: Clang, 
    file: Path | UnresolvedPath = UnresolvedPath('clang++')
) -> None:
    self.file               = file if isinstance(file, Path) else file.resolved_path()
    self.version            = await self._async_get_version()
    self.stdlib_name        = await self._async_get_stdlib_name()
    self.stdlib_module_file = await self._async_get_stdlib_module_file()
    self.compile_flags = [
       f'-std={config.std}',
       f'-stdlib={self.stdlib_name}',
        *(['-O0', '-g'] if config.type == 'debug'   else
          ['-O3']       if config.type == 'release' else
          ['-Os']       if config.type == 'size'    else 
          [])
    ]
    self.link_flags = [
        *(['-s']          if config.type == 'release' or config.type == 'size' else []),
        *(['-lstdc++exp'] if self.stdlib_name == 'libstdc++'                   else [])
    ]
    self.define_macros = {
        **({'DEBUG' : 'true'} if config.type == 'debug'   else 
           {'NDEBUG': 'true'} if config.type == 'release' else 
           {})
    }

@member(Clang)
@syncable
async def async_precompile(
    self            : Clang, 
    module_file     : Path, 
    precompiled_file: Path, 
    object_file     : Path, 
    compile_flags   : list[str]      = [], 
    define_macros   : dict[str, str] = {}, 
    include_dirs    : list[Path]     = [], 
    import_dirs     : list[Path]     = [], 
    diagnostic_file : Path | None    = None
) -> None:
    create_dir(precompiled_file.parent_path())
    create_dir(object_file     .parent_path())
    await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            *[f'-fprebuilt-module-path={import_dir}' for import_dir in import_dirs],
            '--precompile', '-x', 'c++-module', module_file,
            '-o', precompiled_file
        ]
    )
    await async_run(
        file=self.file,
        args=[
            *[f'-fprebuilt-module-path={import_dir}' for import_dir in import_dirs],
            '-c', module_file,
            '-o', object_file
        ]
    )

@member(Clang)
@syncable
async def async_compile(
    self: Clang, 
    source_file    : Path, 
    object_file    : Path, 
    compile_flags  : list[str]      = [], 
    define_macros  : dict[str, str] = {}, 
    include_dirs   : list[Path]     = [], 
    import_dirs    : list[Path]     = [], 
    diagnostic_file: Path | None    = None
) -> None:
    create_dir(object_file.parent_path())
    await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            *[f'-fprebuilt-module-path={import_dir}' for import_dir in import_dirs],
            '-c', '-x', 'c++', source_file,
            '-o', object_file
        ]
    )

@member(Clang)
async def _async_get_version(self: Clang):
    try:
        stdout = await async_run(
            file=self.file,
            args=['--version'],
            return_stdout=True
        )
    except SubprocessError as error:
        raise ConfigError(f'clang check failed (with file = {self.file})') from error
    if not stdout.startswith('clang') and 'clang version' not in stdout:
        raise ConfigError(f'clang check failed (with file = {self.file}, subprocess = "{self.file} --version", stdout = "{stdout.splitlines()[0]} ...", requires = "clang++ ..." or "... clang version ...")')
    version = Version.parse(stdout)
    if version < 21:
        raise ConfigError(f'clang version is too old (with file = {self.file}, version = {version}, requires = 21+)')
    return version

async def _async_get_stdlib_name(self: Clang):
    stderr = await async_run(
        file=self.file,
        args=[
            *self.compile_flags,
            '-v',
        ],
        return_stderr=True
    )
    if 'selected gcc installation' in stderr.lower():
        return 'libstdc++'
    else:
        return 'libc++'    

async def _async_get_stdlib_module_file(self: Clang):
    if self.stdlib_name == 'libc++':
        resource_dir = await async_run(
            file=self.file,
            args=['--print-resource-dir'],
            return_stdout=True,
        )
        resource_dir = Path(resource_dir.strip())
        search_file = resource_dir/'..'/'..'/'..'/'share'/'libc++'/'v1'/'std.cppm'
        if exist_file(search_file): 
            return search_file
        else:
            raise ConfigError(f'libc++ module_file is not found (with search_file = {search_file})')
    elif self.stdlib_name == 'libstdc++':
        return await Gcc._async_get_stdlib_module_file(self)
    else:
        assert False
