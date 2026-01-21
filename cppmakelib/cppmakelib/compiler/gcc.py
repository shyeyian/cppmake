from cppmakelib.basic.config         import config
from cppmakelib.error.config         import ConfigError
from cppmakelib.error.subprocess     import SubprocessError
from cppmakelib.execution.run        import async_run
from cppmakelib.file.file_system     import Path, UnresolvedPath, create_dir, exist_file
from cppmakelib.logger.module_mapper import module_mapper_logger
from cppmakelib.system.all           import system
from cppmakelib.utility.decorator    import member, syncable, unique
from cppmakelib.utility.version      import Version
import re
import typing

class Gcc:
    def           __init__    (self, file: Path | UnresolvedPath = UnresolvedPath('g++'))                                                                                                                                                                                -> None      : ...
    async def    __ainit__    (self, file: Path | UnresolvedPath = UnresolvedPath('g++'))                                                                                                                                                                                -> None      : ...
    def             preprocess(self, unit_file  : Path, intermediate_file: Path | None = None,      compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [])                                                                    -> None | str: ...
    async def async_preprocess(self, unit_file  : Path, intermediate_file: Path | None = None,      compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [])                                                                    -> None | str: ...
    def             precompile(self, module_file: Path, interface_file   : Path, object_file: Path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [], import_dirs: list[Path] = [], diagnostic_file: Path | None = None) -> None      : ...
    async def async_precompile(self, module_file: Path, interface_file   : Path, object_file: Path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [], import_dirs: list[Path] = [], diagnostic_file: Path | None = None) -> None      : ...
    def             compile   (self, source_file: Path,                          object_file: Path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [], import_dirs: list[Path] = [], diagnostic_file: Path | None = None) -> None      : ...
    async def async_compile   (self, source_file: Path,                          object_file: Path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = [], import_dirs: list[Path] = [], diagnostic_file: Path | None = None) -> None      : ...
    def             link      (self, object_file: Path, executable_file  : Path,                    link_flags   : list[str] = [],                                     link_files  : list[Path] = [])                                                                    -> None      : ...
    async def async_link      (self, object_file: Path, executable_file  : Path,                    link_flags   : list[str] = [],                                     link_files  : list[Path] = [])                                                                    -> None      : ...
    name               : str = 'gcc'
    preprocessed_suffix: str = '.i'
    precompiled_suffix : str = '.gcm'
    file               : Path
    version            : Version
    stdlib_name        : str = 'libstdc++'
    stdlib_module_file : Path
    stdlib_static_file : Path
    stdlib_shared_file : Path
    compile_flags      : list[str]
    link_flags         : list[str]
    define_macros      : dict[str, str]

    async def _async_get_version           (self) -> Version: ...
    async def _async_get_stdlib_module_file(self) -> Path   : ...

    if typing.TYPE_CHECKING:
        @typing.overload
        def             preprocess(self, unit_file: Path, intermediate_file: Path,        compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = []) -> None: ...
        @typing.overload
        def             preprocess(self, unit_file: Path, intermediate_file: None = None, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = []) -> str: ...
        @typing.overload
        async def async_preprocess(self, unit_file: Path, intermediate_file: Path,        compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = []) -> None: ...
        @typing.overload
        async def async_preprocess(self, unit_file: Path, intermediate_file: None = None, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[Path] = []) -> str: ...



@member(Gcc)
@syncable
@unique
async def __ainit__(
    self: Gcc, 
    file: Path | UnresolvedPath = UnresolvedPath('g++')
) -> None:
    self.file               = file if isinstance(file, Path) else file.resolved_path()
    self.version            = await self._async_get_version()
    self.stdlib_module_file = await self._async_get_stdlib_module_file()
    self.compile_flags = [
       f'-std={config.std}', '-fmodules', 
        *(['-O0', '-g'] if config.type == 'debug'   else
          ['-O3']       if config.type == 'release' else
          ['-Os']       if config.type == 'size'    else 
          []) 
    ]
    self.link_flags = [
       f'-fuse-ld={system.linker}',
        *(['-s'] if config.type == 'release' or config.type == 'size' else []),
        '-lstdc++exp'
    ]
    self.define_macros = {
        **({'DEBUG'  : 'true'} if config.type == 'debug'   else
           {'DNDEBUG': 'true'} if config.type == 'release' else
           {})
    }

@member(Gcc)
@syncable
async def async_preprocess(
    self             : Gcc, 
    unit_file        : Path, 
    intermediate_file: Path | None = None, 
    compile_flags    : list[str]      = [], 
    define_macros    : dict[str, str] = {}, 
    include_dirs     : list[Path]     = []
) -> None | str:
    return await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            '-E', unit_file,
            '-o', intermediate_file if intermediate_file is not None else '-'
        ],
        print_stdout=False,
        return_stdout=intermediate_file is None
    )

@member(Gcc)
@syncable
async def async_precompile(
    self            : Gcc, 
    module_file     : Path, 
    precompiled_file: Path, 
    object_file     : Path, 
    compile_flags   : list[str]      = [], 
    define_macros   : dict[str, str] = {}, 
    include_dirs    : list[str]      = [], 
    import_dirs     : list[Path]     = [], 
    diagnostic_file : Path | None    = None
):
    create_dir(precompiled_file.parent_path())
    create_dir(object_file     .parent_path())
    create_dir(diagnostic_file .parent_path()) if diagnostic_file is not None else None
    await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            *[f'-fmodule-mapper={module_mapper_logger.get_mapper(import_dir)}' for import_dir in import_dirs],
            *([f'-fdiagnostics-add-output=sarif:code_file={diagnostic_file}'] if diagnostic_file is not None else []),
            '-c', '-x', 'c++-module', module_file,
            '-o', object_file
        ]
    )

@member(Gcc)
@syncable
async def async_compile(
    self           : Gcc, 
    source_file    : Path,
    object_file    : Path,
    compile_flags  : list[str] = [],
    define_macros  : dict[str, str] = {}, 
    include_dirs   : list[Path] =[], 
    import_dirs    : list[Path] = [], 
    diagnostic_file: Path | None = None
) -> None:
    create_dir(object_file    .parent_path())
    create_dir(diagnostic_file.parent_path()) if diagnostic_file is not None else None
    await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            *[f'-fmodule-mapper={module_mapper_logger.get_mapper(import_dir)}' for import_dir in import_dirs],
            *([f'-fdiagnostics-add-output=sarif:code_file={diagnostic_file}'] if diagnostic_file is not None else []),
            '-c', '-x', 'c++', source_file,
            '-o', object_file
        ]
    )

@member(Gcc)
@syncable
async def async_link(
    self           : Gcc, 
    object_file    : Path, 
    executable_file: Path, 
    link_flags     : list[str]  = [], 
    link_files     : list[Path] = []
) -> None:
    create_dir(executable_file.parent_path())
    await async_run(
        file=self.file,
        args=[
            *(self.link_flags + link_flags),
            *([object_file] + link_files),
            '-o', executable_file
        ]
    )

@member(Gcc)
async def _async_get_version(self: Gcc) -> Version:
    try:
        stdout = await async_run(
            file=self.file,
            args=['--version'],
            return_stdout=True
        )
    except SubprocessError as error:
        raise ConfigError(f'gcc check failed (with file = {self.file})') from error
    if not stdout.startswith('g++'):
        raise ConfigError(f'gcc check failed (with file = {self.file}, subprocess = "{self.file} --version", stdout = "{stdout.splitlines()[0]} ...", requires = "g++ ...")')
    version = Version.parse(stdout)
    if version < 15:
        raise ConfigError(f'gcc version is too old (with file = {self.file}, version = {version}, requires = 15+)')
    return version

@member(Gcc)
async def _async_get_stdlib_module_file(self: Gcc) -> Path:
    stderr = await async_run(
        file=self.file,
        args=[
            *self.compile_flags,
            '-E', '-x', 'c++', '-',
            '-v' 
        ], 
        print_stderr =config.verbose, 
        return_stderr=True
    )
    search_dirs = re.search(
        pattern=r'^#include <...> search starts here:$\n(.*)\n^end of search list.$', 
        string=stderr, 
        flags=re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    if search_dirs is None:
        raise ConfigError(f'libstdc++ module_file is not found (with subprocess = "{self.file} -v -E -x c++ -", stdout = ..., requires = "... #include <...> starts here ... end of search list ...")')
    search_dirs  = [Path(search_dir.strip())   for search_dir in search_dirs.group(1).splitlines()]
    search_files = [search_dir/'bits'/'std.cc' for search_dir in search_dirs]
    for search_file in search_files:
        if exist_file(search_file):
            return search_file
    else:
        raise ConfigError(f'libstdc++ module_file is not found (with search_files = {search_files})')
