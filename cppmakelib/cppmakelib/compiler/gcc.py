from cppmakelib.basic.config          import config
from cppmakelib.error.config          import ConfigError
from cppmakelib.error.subprocess      import SubprocessError
from cppmakelib.execution.run         import async_run
from cppmakelib.file.file_system      import parent_path, exist_file, create_dir
from cppmakelib.logger.module_mapper  import module_mapper_logger
from cppmakelib.system.all            import system
from cppmakelib.utility.decorator     import member, syncable
from cppmakelib.utility.version       import parse_version
import re

class Gcc:
    name          = "gcc"
    import_suffix = ".gcm"
    object_suffix = ".o"
    def           __init__                (self, path="g++"):                                                                                                                     ...
    async def     __ainit__               (self, path="g++"):                                                                                                                     ...
    def             preprocess            (self, code_file,                             include_dirs=[],                 compile_flags=[], define_macros={}):                     ...
    async def async_preprocess            (self, code_file,                             include_dirs=[],                 compile_flags=[], define_macros={}):                     ...
    def             precompile            (self, code_file,   import_file, object_file, import_dirs=[], include_dirs=[], compile_flags=[], define_macros={}, diagnose_file=None): ...
    async def async_precompile            (self, code_file,   import_file, object_file, import_dirs=[], include_dirs=[], compile_flags=[], define_macros={}, diagnose_file=None): ...
    def             compile               (self, code_file,   object_file,              import_dirs=[], include_dirs=[], compile_flags=[], define_macros={}, diagnose_file=None): ...
    async def async_compile               (self, code_file,   object_file,              import_dirs=[], include_dirs=[], compile_flags=[], define_macros={}, diagnose_file=None): ...
    def             link_executable       (self, object_file, executable_file,          link_files =[],                  link_flags=[]):                                          ...
    async def async_link_executable       (self, object_file, executable_file,          link_files =[],                  link_flags=[]):                                          ...
    def             get_version           (self):                                                                                                                                 ...
    async def async_get_version           (self):                                                                                                                                 ...
    def             get_stdlib_name       (self):                                                                                                                                 ...
    async def async_get_stdlib_name       (self):                                                                                                                                 ...
    def             get_stdlib_import_file(self):                                                                                                                                 ...
    async def async_get_stdlib_import_file(self):                                                                                                                                 ...
    def             get_stdlib_include_dir(self):                                                                                                                                 ...
    async def async_get_stdlib_include_dir(self):                                                                                                                                 ...



@member(Gcc)
@syncable
async def __ainit__(self, path="g++"):
    self.path        = path
    self.version     = await self.async_get_version()
    self.stdlib_name = await self.async_get_default_stdlib_name()
    self.compile_flags = [
        f"-std={config.std}", "-fmodules", 
         *(["-O0", "-g"] if config.type == "debug"   else
           ["-O3",     ] if config.type == "release" else
           ["-Os"      ] if config.type == "size"    else 
           []) 
    ]
    self.link_flags = [
        *([f"-fuse-ld={system.linker_path}"] if system.linker_path != "ld"                        else []),
        *(["-s"                            ] if config.type == "release" or config.type == "size" else []),
        "-lstdc++exp"
    ]
    self.define_macros = {
        **({"DEBUG"  : "true"} if config.type == "debug"   else
           {"DNDEBUG": "true"} if config.type == "release" else
           {})
    }

@member(Gcc)
@syncable
async def async_preprocess(self, code_file, include_dirs=[], compile_flags=[], define_macros={}):
    return await async_run(
        command=[
            self.path,
            *(self.compile_flags + compile_flags),
            *[f"-I{include_dir}" for include_dir in include_dirs],
            *[f"-D{key}={value}" for key, value  in (self.define_macros | define_macros).items()],
            "-E", code_file,
            "-o", "-"
        ],
        print_stdout=False,
        return_stdout=True
    )

@member(Gcc)
@syncable
async def async_precompile(self, code_file, import_file, object_file, import_dirs=[], include_dirs=[], compile_flags=[], define_macros={}, diagnose_file=None):
    create_dir(parent_path(import_file))
    create_dir(parent_path(object_file))
    create_dir(parent_path(diagnose_file)) if diagnose_file is not None else None
    await async_run(
        command=[
            self.path,
            *(self.compile_flags + compile_flags),
            *[f"-fmodule-mapper={module_mapper_logger.get_mapper(import_dir)}" for import_dir  in import_dirs                                 ],
            *[f"-I{include_dir}"                                               for include_dir in include_dirs                                ],
            *[f"-D{key}={value}"                                               for key, value  in (self.define_macros | define_macros).items()],
            *([f"-fdiagnostics-add-output=sarif:code_file={diagnose_file}"] if diagnose_file is not None else []),
            "-c", code_file,
            "-o", object_file
        ],
        log_command=(True, code_file)
    )

@member(Gcc)
@syncable
async def async_compile(self, code_file, object_file, import_dirs=[], include_dirs=[], compile_flags=[], link_flags=[], define_macros={}, diagnose_file=None):
    create_dir(parent_path(object_file))
    create_dir(parent_path(diagnose_file)) if diagnose_file is not None else None
    await async_run(
        command=[
            self.path,
            *(self.compile_flags + compile_flags),
            *[f"-fmodule-mapper={module_mapper_logger.get_mapper(import_dir)}" for import_dir  in import_dirs                                 ],
            *[f"-I{include_dir}"                                               for include_dir in include_dirs                                ],
            *[f"-D{key}={value}"                                               for key, value  in (self.define_macros | define_macros).items()],
            *([f"-fdiagnostics-add-output=sarif:code_file={diagnose_file}"] if diagnose_file is not None else []),
            "-c", code_file,
            "-o", object_file
        ],
        log_command=(True, code_file)
    )

@member(Gcc)
@syncable
async def async_link_executable(self, object_file, executable_file, link_files=[], link_flags=[]):
    create_dir(parent_path(executable_file))
    await async_run(
        command=[
            self.path,
            *(self.link_flags + link_flags),
            object_file,
            *link_files
        ]
    )

@member(Gcc)
@syncable
async def async_get_version(self):
    try:
        version_str = await async_run(command=[self.path, "--version"], return_stdout=True)
        if version_str.startswith("g++"):
            version = parse_version(version_str)
            if version >= 15:
                return version
            else:
                raise ConfigError(f'gcc is too old (with version = {version}, requires >= 15)')
        else:
            raise ConfigError(f'gcc is not valid (with "{self.path} --version" outputs "{version_str.replace('\n', ' ')}")')
    except SubprocessError as error:
        raise ConfigError(f'gcc is not valid (with "{self.path} --version" outputs "{error.stderr.replace('\n', ' ')}" and exits {error.code})')
    except FileNotFoundError as error:
        raise ConfigError(f'gcc is not found (with "{self.path} --version" fails "{error}")')
    
@member(Gcc)
@syncable
async def async_get_default_stdlib_name(self):
    return "libstdc++"

@member(Gcc)
@syncable
async def async_get_stdlib_file(self):
    verbose_info = await async_run(
        command=[
            self.path,
            *self.compile_flags,
            "-E", "-x", "c++", "-"
            "-v" 
        ], 
        input_stdin="", 
        print_stderr=config.verbose, 
        return_stderr=True
    )
    search_dirs = re.search(r'^#include <...> search starts here:$\n(.*)\n^end of search list.$', verbose_info, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if search_dirs is None:
        raise ConfigError(f'libstdc++ module not found (with "{self.path} -v -E -x c++ -" outputs [[invalid message]])')
    search_dirs = [search_dir.strip() for search_dir in search_dirs.group(1).splitlines()]
    for include_dir in search_dirs:
        import_file = f"{include_dir}/bits/std.cc"
        if exist_file(import_file):
            return import_file
    else:
        raise ConfigError(f"libstdc++ module not found (with search_file = {', '.join([f"{include_dir}/bits/std.cc" for include_dir in search_dirs])})")
        