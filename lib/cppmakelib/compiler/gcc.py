class Gcc:
    def           __init__    (self, file: path = 'g++')                                                                                                                                                                                                                 -> None: ...
    async def    __ainit__    (self, file: path = 'g++')                                                                                                                                                                                                                 -> None: ...
    def             preprocess(self, code_file  : path, preprocessed_file: path,                    compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [])                                                                    -> None: ...
    async def async_preprocess(self, code_file  : path, preprocessed_file: path,                    compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [])                                                                    -> None: ...
    def             preparse  (self, header_file: path, preparsed_file   : path,                    compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [],                               diagnostic_file: path | None = None) -> None: ...
    async def async_preparse  (self, header_file: path, preparsed_file   : path,                    compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [],                               diagnostic_file: path | None = None) -> None: ...
    def             precompile(self, module_file: path, precompiled_file : path, object_file: path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [], import_dirs: list[path] = [], diagnostic_file: path | None = None) -> None: ...
    async def async_precompile(self, module_file: path, precompiled_file : path, object_file: path, compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [], import_dirs: list[path] = [], diagnostic_file: path | None = None) -> None: ...
    def             compile   (self, source_file: path, object_file      : path,                    compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [], import_dirs: list[path] = [], diagnostic_file: path | None = None) -> None: ...
    async def async_compile   (self, source_file: path, object_file      : path,                    compile_flags: list[str] = [], define_macros: dict[str, str] = {}, include_dirs: list[path] = [], import_dirs: list[path] = [], diagnostic_file: path | None = None) -> None: ...
    def             share     (self, object_file: path, dynamic_file     : path,                    link_flags   : list[str] = [],                                     lib_files   : list[path] = [])                                                                    -> None: ...
    async def async_share     (self, object_file: path, dynamic_file     : path,                    link_flags   : list[str] = [],                                     lib_files   : list[path] = [])                                                                    -> None: ...
    def             link      (self, object_file: path, executable_file  : path,                    link_flags   : list[str] = [],                                     lib_files   : list[path] = [])                                                                    -> None: ...
    async def async_link      (self, object_file: path, executable_file  : path,                    link_flags   : list[str] = [],                                     lib_files   : list[path] = [])                                                                    -> None: ...
    preprocessed_suffix: str = '.ipp'
    preparsed_suffix   : str = '.gch'
    precompiled_suffix : str = '.gcm'  
    diagnostic_suffix  : str = '.sarif'
    file               : path
    version            : Version
    compile_flags      : list[str]
    link_flags         : list[str]
    define_macros      : dict[str, str]
    stdlib_name        : str = 'libstdc++'
    stdlib_module_file : path
    stdlib_static_file : path
    stdlib_dynamic_file: path

    async def _async_get_version           (self)                                             -> Version: ...
    async def _async_get_stdlib_module_file(self)                                             -> path   : ...
    def       _write_mapper                (self, target_file: path, import_dirs: list[path]) -> path   : ...



from cppmakelib.basic.config         import config
from cppmakelib.error.config         import ConfigError
from cppmakelib.error.subprocess     import SubprocessError
from cppmakelib.executor.run         import async_run
from cppmakelib.utility.decorator    import member, syncable
from cppmakelib.utility.filesystem   import create_dir, exist_file, iterate_dir, parent_dir, path
from cppmakelib.utility.version      import Version
import re

@member(Gcc)
@syncable
async def __ainit__(self: Gcc, file: path = 'g++') -> None:
    self.file               = file
    self.version            = await self._async_get_version()
    self.compile_flags = [
        f'-std={config.std}', '-fmodules', 
        *(['-O0', '-g'] if config.type == 'debug'   else
          ['-O3']       if config.type == 'release' else
          ['-Os']       if config.type == 'size'    else 
          []) 
    ]
    self.link_flags = [
        *(['-s'] if config.type == 'release' or config.type == 'size' else []),
        '-lstdc++exp'
    ]
    self.define_macros = {
        **({'DEBUG'  : 'true'} if config.type == 'debug'   else
           {'DNDEBUG': 'true'} if config.type == 'release' else
           {})
    }
    self.stdlib_module_file = await self._async_get_stdlib_module_file()

@member(Gcc)
@syncable
async def async_preprocess(
    self             : Gcc, 
    unit_file        : path, 
    preprocessed_file: path, 
    compile_flags    : list[str]      = [], 
    define_macros    : dict[str, str] = {}, 
    include_dirs     : list[path]     = []
) -> None:
    await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            '-E', unit_file,
            '-o', preprocessed_file
        ],
        print_stdout=False,
    )

@member(Gcc)
@syncable
async def async_preparse(
    self           : Gcc,
    header_file    : path,
    preparsed_file : path,
    compile_flags  : list[str]      = [],
    define_macros  : dict[str, str] = {},
    include_dirs   : list[path]     = [],
    diagnostic_file: path | None    = None
) -> None:
    create_dir(parent_dir(preparsed_file))
    create_dir(parent_dir(diagnostic_file)) if diagnostic_file is not None else None
    await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            *([f'-fdiagnostics-add-output=sarif:file={diagnostic_file}'] if diagnostic_file is not None else []),
            '-c', '-x', 'c++-header', header_file,
            '-o', preparsed_file
        ],
        log_command=header_file
    )
    

@member(Gcc)
@syncable
async def async_precompile(
    self            : Gcc, 
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
    create_dir(parent_dir(diagnostic_file)) if diagnostic_file is not None else None
    await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            f'-fmodule-mapper={self._write_mapper(target_file=precompiled_file, import_dirs=import_dirs)}',
            *([f'-fdiagnostics-add-output=sarif:file={diagnostic_file}'] if diagnostic_file is not None else []),
            '-c', '-x', 'c++-module', module_file,
            '-o', object_file
        ],
        log_command=module_file
    )

@member(Gcc)
@syncable
async def async_compile(
    self           : Gcc, 
    source_file    : path,
    object_file    : path,
    compile_flags  : list[str]      = [],
    define_macros  : dict[str, str] = {}, 
    include_dirs   : list[path]     = [], 
    import_dirs    : list[path]     = [], 
    diagnostic_file: path | None = None
) -> None:
    create_dir(parent_dir(object_file))
    create_dir(parent_dir(diagnostic_file)) if diagnostic_file is not None else None
    await async_run(
        file=self.file,
        args=[
            *(self.compile_flags + compile_flags),
            *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
            *[f'-I{include_dir}' for include_dir in include_dirs],
            f'-fmodule-mapper={self._write_mapper(target_file=object_file, import_dirs=import_dirs)}',
            *([f'-fdiagnostics-add-output=sarif:file={diagnostic_file}'] if diagnostic_file is not None else []),
            '-c', '-x', 'c++', source_file,
            '-o', object_file
        ],
        log_command=source_file
    )

@member(Gcc)
@syncable
async def async_link(
    self           : Gcc, 
    object_file    : path, 
    executable_file: path, 
    link_flags     : list[str]  = [], 
    lib_files      : list[path] = []
) -> None:
    create_dir(parent_dir(executable_file))
    await async_run(
        file=self.file,
        args=[
            *(self.link_flags + link_flags),
            *([object_file] + lib_files),
            '-o', executable_file
        ]
    )

@member(Gcc)
async def _async_get_version(self: Gcc) -> Version:
    try:
        stdout = await async_run(
            file=self.file,
            args=['--version'],
            print_stdout=config.verbose,
            return_stdout=True
        )
    except SubprocessError as error:
        raise ConfigError(f'gcc check failed (with file = {self.file})') from error
    try:
        version = Version.parse(pattern=r'^g\+\+\w* \(.*\) (\d+)\.(\d+)\.(\d+)', string=stdout.splitlines()[0])
    except Version.ParseError as error:
        raise ConfigError(f'gcc check failed (with file = {self.file})') from error
    if version < 15:
        raise ConfigError(f'gcc version is too old (with file = {self.file}, version = {version}, requires = 15+)')
    return version

@member(Gcc)
async def _async_get_stdlib_module_file(self: Gcc) -> path:
    stderr = await async_run(
        file=self.file,
        args=[
            *self.compile_flags,
            '-E', '-x', 'c++', '-',
            '-v' 
        ],
        print_stderr=config.verbose,
        return_stderr=True
    )
    search_dirs = re.search(
        pattern=r'^#include <...> search starts here:$\n((?:^.*$\n)*)^End of search list.$', 
        string =stderr, 
        flags  =re.MULTILINE
    )
    if search_dirs is None:
        raise ConfigError(f'libstdc++ module_file is not found')
    search_dirs  = [path(search_dir.strip())    for search_dir in search_dirs.group(1).splitlines()]
    search_files = [f'{search_dir}/bits/std.cc' for search_dir in search_dirs]
    for search_file in search_files:
        if exist_file(search_file):
            return search_file
    else:
        raise ConfigError(f'libstdc++ module_file is not found (with search_files = {search_files})')

@member(Gcc)
def _write_mapper(self: Gcc, target_file: path, import_dirs: list[path]) -> path:
    mapper_file = f'{target_file.rpartition('.')[0]}.mapper'
    writer = open(mapper_file, 'w')
    for import_dir in import_dirs:
        for file in iterate_dir(import_dir):
            name = file.split('/')[-1].removesuffix(self.precompiled_suffix).replace('-', ':') # TODO: get rid of split('/').
            writer.write(f'{name} {file}\n')
    writer.close()
    return mapper_file
    