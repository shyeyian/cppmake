from cppmakelib.basic.config       import config
from cppmakelib.compiler.gcc       import Gcc
from cppmakelib.error.config       import ConfigError
from cppmakelib.error.subprocess   import SubprocessError
from cppmakelib.executor.run       import async_run
from cppmakelib.utility.decorator  import member, syncable, unique
from cppmakelib.utility.filesystem import create_dir, exist_file, parent_dir, path
from cppmakelib.utility.version    import Version

class Clang(Gcc):
    def           __init__    (self, file: path = 'clang++')                                                                                                                                                                           -> None: ...
    async def    __ainit__    (self, file: path = 'clang++')                                                                                                                                                                           -> None: ...
    def             precompile(self, module_file: path, precompiled_file: path, object_file: path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [], import_dirs: list[path] = [], diagnostic_file: path | None = None) -> None: ...
    async def async_precompile(self, module_file: path, precompiled_file: path, object_file: path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [], import_dirs: list[path] = [], diagnostic_file: path | None = None) -> None: ...
    def             compile   (self, source_file: path, object_file     : path,                    compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [], import_dirs: list[path] = [], diagnostic_file: path | None = None) -> None: ...
    async def async_compile   (self, source_file: path, object_file     : path,                    compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [], import_dirs: list[path] = [], diagnostic_file: path | None = None) -> None: ...
    precompiled_suffix: str = '.pcm'
    file              : path
    version           : Version
    stdlib_name       : str
    stdlib_module_file: path
    stdlib_static_file: path
    stdlib_shared_file: path
    compile_flags     : list[str]
    link_flags        : list[str]
    define_macros     : dict[str, str]

    async def _async_get_version           (self) -> Version: ...
    async def _async_get_stdlib_name       (self) -> str: ...
    async def _async_get_stdlib_module_file(self) -> path   : ...



@member(Clang)
@syncable
@unique
async def __ainit__(
    self: Clang, 
    file: path = 'clang++'
) -> None:
    self.file               = file
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
    module_file     : path, 
    precompiled_file: path, 
    object_file     : path, 
    compile_flags   : list[str]      = [], 
    define_macros   : dict[str, str] = {}, 
    include_dirs    : list[path]     = [], 
    import_dirs     : list[path]     = [], 
    diagnostic_file : path | None    = None
) -> None:
    create_dir(parent_dir(precompiled_file))
    create_dir(parent_dir(object_file))
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
    source_file    : path, 
    object_file    : path, 
    compile_flags  : list[str]      = [], 
    define_macros  : dict[str, str] = {}, 
    include_dirs   : list[path]     = [], 
    import_dirs    : list[path]     = [], 
    diagnostic_file: path | None    = None
) -> None:
    create_dir(parent_dir(object_file))
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
async def _async_get_version(self: Clang) -> Version:
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

async def _async_get_stdlib_name(self: Clang) -> str:
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

async def _async_get_stdlib_module_file(self: Clang) -> path:
    if self.stdlib_name == 'libc++':
        resource_dir = await async_run(
            file=self.file,
            args=['--print-resource-dir'],
            return_stdout=True,
        )
        resource_dir = path(resource_dir.strip())
        search_file = f'{resource_dir}/../../../share/libc++/v1/std.cppm'
        if exist_file(search_file): 
            return search_file
        else:
            raise ConfigError(f'libc++ module_file is not found (with search_file = {search_file})')
    elif self.stdlib_name == 'libstdc++':
        return await Gcc._async_get_stdlib_module_file(self)
    else:
        assert False
