from cppmakelib.basic.config          import config
from cppmakelib.error.config          import ConfigError
from cppmakelib.error.subprocess      import SubprocessError
from cppmakelib.execution.run         import async_run
from cppmakelib.file.file_system      import parent_path, create_dir
from cppmakelib.logger.module_mapper  import module_mapper_logger
from cppmakelib.utility.decorator     import member, syncable
from cppmakelib.utility.version       import parse_version



class Gcc:
    name          = "gcc"
    module_suffix = ".gcm"
    object_suffix = ".o"
    def           __init__    (self, path="g++"):                                                                                          ...
    async def     __ainit__   (self, path="g++"):                                                                                          ...
    def             preprocess(self, code,                                                            compile_flags=[], define_macros={}): ...
    async def async_preprocess(self, code,                                                            compile_flags=[], define_macros={}): ...
    def             precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}): ...
    async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}): ...
    def             compile   (self, file,              object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}): ...
    async def async_compile   (self, file,              object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}): ...
    def             link      (self, file, executable_file,                          link_files  =[], link_flags   =[]                  ): ...
    async def async_link      (self, file, executable_file,                          link_files  =[], link_flags   =[]                  ): ...



@member(Gcc)
@syncable
async def __ainit__(self, path="g++"):
    self.path = path
    self.version = await self._async_get_version()
    self.compile_flags = [
        f"-std={config.std}", "-fmodules", 
         "-fdiagnostics-color=always", #"-fdiagnostics-format=sarif-stderr",
         "-Wall",
         *(["-O0", "-g", "-fno-inline"] if config.type == "debug"   else
           ["-O3",                    ] if config.type == "release" else
           ["-Os"                     ] if config.type == "size"    else 
           []) 
    ]
    self.link_flags = [
        "-lstdc++exp",
        *(["-s"] if config.type == "release" or config.type == "size" else [])
    ]
    self.define_macros = {
        **({"DEBUG"  : "true"} if config.type == "debug"   else
           {"DNDEBUG": "true"} if config.type == "release" else
           {})
    }

@member(Gcc)
@syncable
async def async_preprocess(self, code, compile_flags=[], define_macros={}):
    return await async_run(
        command=[
            self.path,
            *(self.compile_flags + compile_flags),
            *[f"-D{key}={value}" for key, value in (self.define_macros | define_macros).items()],
            "-E", "-x", "c++", "-",
            "-o", "-"
        ],
        input_stdin=code,
        print_stdout=False,
        return_stdout=True
    )

@member(Gcc)
@syncable
async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}):
    create_dir(parent_path(module_file))
    create_dir(parent_path(object_file))
    await async_run(
        command=[
            self.path,
            *(self.compile_flags + compile_flags),
            *[f"-fmodule-mapper={module_mapper_logger.get_mapper(module_dir)}" for module_dir  in module_dirs                                 ],
            *[f"-I{include_dir}"                                               for include_dir in include_dirs                                ],
            *[f"-D{key}={value}"                                               for key, value  in (self.define_macros | define_macros).items()],
            "-c", file,
            "-o", object_file
        ],
        log_command=(True, file),
        log_stderr =True
    )

@member(Gcc)
@syncable
async def async_compile(self, file, object_file, include_dirs=[], module_dirs=[], link_files=[], compile_flags=[], define_macros={}):
    create_dir(parent_path(object_file))
    await async_run(
        command=[
            self.path,
            *(self.compile_flags + compile_flags),
            *[f"-fmodule-mapper={module_mapper_logger.get_mapper(module_dir)}" for module_dir  in module_dirs                                 ],
            *[f"-I{include_dir}"                                               for include_dir in include_dirs                                ],
            *[f"-D{key}={value}"                                               for key, value  in (self.define_macros | define_macros).items()],
            "-c", file,
            "-o", object_file
        ],
        log_command=(True, file),
        log_stderr =True
    )

@member(Gcc)
@syncable
async def async_link(self, file, executable_file, link_files=[], link_flags=[]):
    create_dir(parent_path(executable_file))
    await async_run(
        command=[
            self.path,
            *(self.link_flags + link_flags),
            file, *link_files,
            "-o", executable_file
        ]
    )

@member(Gcc)
async def _async_get_version(self):
    try:
        version_str = await async_run(command=[self.path, "--version"], return_stdout=True)
        if "gcc" not in version_str.lower() or "emcc" in version_str.lower():
            raise ConfigError(f'gcc is not valid (with "{self.path} --version" outputs "{version_str.replace('\n', ' ')}")')
        version = parse_version(version_str)
        if version < 15:
            raise ConfigError(f'gcc is too old (with version = {version}, requires >= 15)')
        return version            
    except SubprocessError as error:
        raise ConfigError(f'gcc is not valid (with "{self.path} --version" outputs "{error.stderr.replace('\n', ' ')}" and exits {error.code})')
    except FileNotFoundError as error:
        raise ConfigError(f'gcc is not found (with "{self.path} --version" fails "{error}")')