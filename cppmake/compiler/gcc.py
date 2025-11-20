from cppmake.basic.config          import config
from cppmake.error.config          import ConfigError
from cppmake.error.subprocess      import SubprocessError
from cppmake.execution.run         import async_run
from cppmake.file.file_system      import parent_path, create_dir
from cppmake.logger.module_mapper  import module_mapper_logger
from cppmake.utility.decorator     import member, syncable


class Gcc:
    name          = "gcc"
    module_suffix = ".gcm"
    object_suffix = ".o"
    def           __init__    (self, path="g++"):                                                                                      ...
    async def     __ainit__   (self, path="g++"):                                                                                      ...
    def             preprocess(self, file,                                                                           defines={}): ...
    async def async_preprocess(self, file,                                                                           defines={}): ...
    def             precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[],                defines={}): ...
    async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[],                defines={}): ...
    def             compile   (self, file, executable_file,          module_dirs=[], include_dirs=[], link_files=[], defines={}): ...
    async def async_compile   (self, file, executable_file,          module_dirs=[], include_dirs=[], link_files=[], defines={}): ...



@member(Gcc)
@syncable
async def __ainit__(self, path="g++"):
    await Gcc._async_check(path)
    self.path = path
    self.compile_flags = [
       f"-std={config.std}", "-fmodules", 
        "-fdiagnostics-colors=always", "-fdiagnostics-format=sarif-stderr",
        "-Wall", "-Wno-global-module", "-Wno-global-module-tu-local-exports", "-Wno-deprecated-variadic-comma-omission",
     *(["-O0", "-g", "-DDEBUG", "-fno-inline"] if config.type == "debug"   else
       ["-O3",       "-DNDEBUG"              ] if config.type == "release" else
       ["-Os"                                ] if config.type == "size"    else 
       []) 
    ]
    self.link_flags = [
        "-lstdc++exp",
     *(["-s"] if config.type == "release" or config.type == "size" else 
       [])
    ]

@member(Gcc)
@syncable
async def async_preprocess(self, code, defines={}):
    return await async_run(
        command=[
            self.path,
           *self.compile_flags,
           *[f"-D{key}={value}" for key, value in defines.items()],
            "-E", "-",
            "-o", "-"
        ],
        input_stdin=code,
        print_stdout=False,
        return_stdout=True
    )

@member(Gcc)
@syncable
async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[], defines={}):
    create_dir(parent_path(module_file))
    create_dir(parent_path(object_file))
    await async_run(
        command=[
            self.path,
           *self.compile_flags,
           *[f"-fmodule-mapper={module_mapper_logger.get_mapper(module_dir)}" for module_dir  in module_dirs    ],
           *[f"-I{include_dir}"                                                for include_dir in include_dirs   ],
           *[f"-D{key}={value}"                                                for key, value  in defines.items()],
            "-c", file,
            "-o", object_file
        ],
        log_command=(True, file),
        log_stderr =True
    )

@member(Gcc)
@syncable
async def async_compile(self, file, executable_file, include_dirs=[], module_dirs=[], link_files=[], defines={}):
    create_dir(parent_path(executable_file))
    await async_run(
        command=[
            self.path,
           *self.compile_flags,
           *[f"-fmodule-mapper={module_mapper_logger.get_mapper(module_dir)}" for module_dir  in module_dirs    ],
           *[f"-I{include_dir}"                                                for include_dir in include_dirs   ],
           *[f"-D{key}={value}"                                                for key, value  in defines.items()],
            file,
           *self.link_flags,
           *link_files,
            "-o", executable_file
        ],
        log_command=(True, file),
        log_stderr =True
    )

@member(Gcc)
async def _async_check(path):
    try:
        version = await async_run(command=[path, "--version"], return_stdout=True)
        if "gcc" not in version.lower():
            raise ConfigError(f'compiler is not gcc (with "{path} --version" outputs "{version.replace('\n', ' ')}")')
    except SubprocessError as error:
        raise ConfigError(f'compiler is not gcc (with "{path} --version" exits {error.code})')