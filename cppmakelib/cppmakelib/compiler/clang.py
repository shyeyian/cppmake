from cppmakelib.basic.config       import config
from cppmakelib.compiler.gcc       import Gcc
from cppmakelib.error.config       import ConfigError
from cppmakelib.error.subprocess   import SubprocessError
from cppmakelib.execution.run      import async_run
from cppmakelib.file.file_system   import parent_path, exist_file, create_dir
from cppmakelib.utility.decorator  import member, once, syncable
from cppmakelib.utility.version    import parse_version
import re

class Clang(Gcc):
    name          = "clang"
    module_suffix = ".pcm"
    object_suffix = ".o"
    def           __init__    (self, path="clang++"):                                                                                                                                                            ...
    async def     __ainit__   (self, path="clang++"):                                                                                                                                                            ...
    def             preprocess(self, file,                                                                           compile_flags=[],                define_macros={}):                                         ...
    async def async_preprocess(self, file,                                                                           compile_flags=[],                define_macros={}):                                         ...
    def             precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[],                compile_flags=[],                define_macros={}, diagnose_file=None, optimize_file=None): ...
    async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[],                compile_flags=[],                define_macros={}, diagnose_file=None, optimize_file=None): ...
    def             compile   (self, file, executable_file,          module_dirs=[], include_dirs=[], link_files=[], compile_flags=[], link_flags=[], define_macros={}, diagnose_file=None, optimize_file=None): ...
    async def async_compile   (self, file, executable_file,          module_dirs=[], include_dirs=[], link_files=[], compile_flags=[], link_flags=[], define_macros={}, diagnose_file=None, optimize_file=None): ...
    def             std_module(self):                                                                                                                                                                            ...
    async def async_std_module(self):                                                                                                                                                                            ...



@member(Clang)
@syncable
async def __ainit__(self, path="clang++"):
    self.path    = path
    self.version = await self._async_get_version()
    self.stdlib  = await self._async_get_stdlib()
    self.compile_flags = [
       f"-std={config.std}",
        "-fdiagnostics-color=always",
        "-Wall", "-Wno-import-implementation-partition-unit-in-interface-unit",
        *(["-O0", "-g", "-fno-inline"] if config.type == "debug"   else
          ["-O3",                    ] if config.type == "release" else
          ["-Os"                     ] if config.type == "size"    else 
          [])
    ]
    self.link_flags = [
        *(["-s"         ] if config.type == "release" or config.type == "size" else []),
        *(["-lstdc++exp"] if self.stdlib == "libstdc++"                        else [])
    ]
    self.define_macros = {
        **({"DEBUG" : "true"} if config.type == "debug"   else 
           {"NDEBUG": "true"} if config.type == "release" else 
           {})
    }

@member(Clang)
@syncable
async def async_preprocess(self, file, compile_flags=[], define_macros={}):
    code = open(file, 'r').read()
    code = re.sub(r'^\s*#include(?!\s*(<version>|<unistd.h>)).*$', "", code, flags=re.MULTILINE)
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

@member(Clang)
@syncable
async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}, diagnose_file=None, optimize_file=None):
    create_dir(parent_path(module_file))
    create_dir(parent_path(object_file))
    create_dir(parent_path(diagnose_file)) if diagnose_file is not None else None
    await async_run(
        command=[
            self.path,
            *(self.compile_flags + compile_flags),
            *[f"-fprebuilt-module-path={module_dir}" for module_dir  in module_dirs                                 ],
            *[f"-I{include_dir}"                     for include_dir in include_dirs                                ],
            *[f"-D{key}={value}"                     for key, value  in (self.define_macros | define_macros).items()],
            *(["-fdiagnostics-format=sarif", "-Wno-sarif-format-unstable"] if diagnose_file is not None else []),
            "--precompile", "-x", "c++-module", file,
            "-o",                               module_file
        ],
        print_stderr=False,
        log_command=(True, file),
        log_stderr =(True, lambda stderr: open(diagnose_file, 'w').write(stderr.splitlines()[-3]) if diagnose_file is not None and stderr != "" else None)
    )
    await async_run(
        command=[
            self.path,
            *[f"-fprebuilt-module-path={module_dir}" for module_dir in module_dirs],
            "-c", module_file,
            "-o", object_file
        ]
    )

@member(Clang)
@syncable
async def async_compile(self, file, executable_file, module_dirs=[], include_dirs=[], link_files=[], compile_flags=[], link_flags=[], define_macros={}, diagnose_file=None, optimize_file=None):
    create_dir(parent_path(executable_file))
    create_dir(parent_path(diagnose_file)) if diagnose_file is not None else None
    await async_run(
        command=[
            self.path,
            *(self.compile_flags + compile_flags),
            *[f"-fprebuilt-module-path={module_dir}" for module_dir  in module_dirs                                 ],
            *[f"-I{include_dir}"                     for include_dir in include_dirs                                ],
            *[f"-D{key}={value}"                     for key, value  in (self.define_macros | define_macros).items()],
            *(["-fdiagnostics-format=sarif", "-Wno-sarif-format-unstable"] if diagnose_file is not None else []),
            file,
            *(self.link_flags + link_flags),
            *link_files,
            "-o", executable_file,
        ],
        print_stderr=False,
        log_command=(True, file),
        log_stderr =(True, lambda stderr: open(diagnose_file, 'w').write(stderr.splitlines()[-3]) if diagnose_file is not None and stderr != "" else None)
    )

@member(Clang)
@syncable
@once
async def async_std_module(self):
    if self.stdlib == "libc++":
        resource_dir = await async_run(
            command=[
                self.path, "--print-resource-dir"
            ],
            return_stdout=True,
        )
        resource_dir = resource_dir.strip()
        module_file  = f"{resource_dir}/../../../share/libc++/v1/std.cppm"
        if exist_file(module_file):
            return module_file
        else:
            raise ConfigError(f'libc++ module not found (with search_file = {module_file})')
    elif self.stdlib == "libstdc++":
        return await Gcc.async_std_module(self)
        
@member(Clang)
async def _async_get_version(self):
    try:
        version_str = await async_run(command=[self.path, "--version"], return_stdout=True)
        if "clang version" in version_str.splitlines()[0]:
            version = parse_version(version_str)
            if version >= 21:
                return version
            else:
                raise ConfigError(f'clang is too old (with version = {version}, requires >= 21')
        else:
            raise ConfigError(f'clang is not valid (with "{self.path} --version" outputs "{version_str.replace('\n', ' ')}")')

    except SubprocessError as error:
        raise ConfigError(f'clang is not valid (with "{self.path} --version" outputs "{error.stderr.replace('\n', ' ')}" and exits {error.code})')
    except FileNotFoundError as error:
        raise ConfigError(f'clang is not found (with "{self.path} --version" fails "{error}")')
    
@member(Clang)
async def _async_get_stdlib(self):
    verbose_info = await async_run(
        command=[
            self.path, "-v"
        ],
        print_stderr=config.verbose,
        return_stderr=True
    )
    if "selected gcc installation" not in verbose_info.lower():
        return "libc++"
    else:
        return "libstdc++"
