from cppmake.basic.config       import config
from cppmake.error.config       import ConfigError
from cppmake.error.subprocess   import SubprocessError
from cppmake.execution.run      import async_run
from cppmake.file.file_system   import parent_path, create_dir
from cppmake.utility.decorator  import member, syncable
from cppmake.utility.sarif      import make_sarif

class Clang:
    name          = "clang"
    module_suffix = ".pcm"
    object_suffix = ".o"
    def           __init__    (self, path="clang++"):                                                                                  ...
    async def     __ainit__   (self, path="clang++"):                                                                                  ...
    def             preprocess(self, file,                                                                           defines={}): ...
    async def async_preprocess(self, file,                                                                           defines={}): ...
    def             precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[],                defines={}): ...
    async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[],                defines={}): ...
    def             compile   (self, file, executable_file,          module_dirs=[], include_dirs=[], link_files=[], defines={}): ...
    async def async_compile   (self, file, executable_file,          module_dirs=[], include_dirs=[], link_files=[], defines={}): ...



@member(Clang)
@syncable
async def __ainit__(self, path="clang++"):
    await Clang._async_check(path)
    self.path = path
    self.compile_flags = [
       f"-std={config.std}",   
        "-fdiagnostics-color=always",
        "-Wall", "-Wno-reserved-module-identifier", "-Wno-deprecated-missing-comma-variadic-parameter",
     *(["-O0", "-g", "-DDEBUG", "-fno-inline"] if config.type == "debug"   else
       ["-O3",       "-DNDEBUG"              ] if config.type == "release" else
       ["-Os"                                ] if config.type == "size"    else 
       [])
    ]
    self.link_flags = [
     *(["-s"] if config.type == "release" or config.type == "size" else 
       [])
    ]

@member(Clang)
@syncable
async def async_preprocess(self, code, defines={}):
    return await async_run(
        command=[
            self.path,
           *self.compile_flags,
           *[f"-D{key}={value}" for key, value in defines.items()],
            "-E", "-x", "c++", "-",
            "-o", "-"
        ],
        input_stdin=code,
        print_stdout=False,
        return_stdout=True
    )

@member(Clang)
@syncable
async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[], defines={}):
    create_dir(parent_path(module_file))
    create_dir(parent_path(object_file))
    await async_run(
        command=[
            self.path,
           *self.compile_flags,
           *[f"-fprebuilt-module-path={module_dir}" for module_dir  in module_dirs    ],
           *[f"-I{include_dir}"                     for include_dir in include_dirs   ],
           *[f"-D{key}={value}"                     for key, value  in defines.items()],
            "--precompile", "-x", "c++-module", file,
            "-o",                               module_file
        ],
        log_command=(True, file),
        log_stderr =(True, make_sarif)
    )
    await async_run(
        command=[
            self.path,
            "-c", module_file,
            "-o", object_file
        ]
    )

@member(Clang)
@syncable
async def async_compile(self, file, executable_file, module_dirs=[], include_dirs=[], link_files=[], defines={}):
    create_dir(parent_path(executable_file))
    await async_run(
        command=[
            self.path,
           *self.compile_flags,
           *[f"-fprebuilt-module-path={module_dir}" for module_dir  in module_dirs    ],
           *[f"-I{include_dir}"                     for include_dir in include_dirs   ],
           *[f"-D{key}={value}"                     for key, value  in defines.items()],
            file,
           *self.link_flags,
           *link_files,
            "-o", executable_file
        ],
        log_command=(True, file),
        log_stderr =(True, make_sarif)
    )

@member(Clang)
async def _async_check(path):
    try:
        version = await async_run(command=[path, "--version"], return_stdout=True)
        if "clang" not in version.lower():
            raise ConfigError(f'compiler is not clang (with "{path} --version" outputs "{version.replace('\n', ' ')}")')
    except SubprocessError as error:
        raise ConfigError(f'compiler is not clang (with "{path} --version" exits {error.code}')