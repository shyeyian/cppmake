from cppmakelib.basic.config      import config
from cppmakelib.compiler.gcc      import Gcc
from cppmakelib.error.config      import ConfigError
from cppmakelib.execution.run     import async_run
from cppmakelib.file.file_system  import parent_path, exist_file, create_dir
from cppmakelib.utility.decorator import unique, syncable
from cppmakelib.utility.version   import Version

class Clang(Gcc):
    name                = 'clang'
    intermediate_suffix = '.i'
    precompiled_suffix  = '.pcm'

    @syncable
    @unique
    async def __ainit__(self, path='clang++'):
        self.path               = path
        self.version            = await self._async_get_version()
        self.stdlib_name        = await self._async_get_stdlib_name()
        self.stdlib_module_file = await self._async_get_stdlib_module_file()
        self.stdlib_static_file = ...
        self.stdlib_shared_file = ...
        self.compile_flags = [
           f'-std={config.std}',
           f'-stdlib={self.stdlib_name}',
            *(['-O0', '-g'] if config.type == 'debug'   else
              ['-O3']       if config.type == 'release' else
              ['-Os']       if config.type == 'size'    else 
              [])
        ]
        self.link_flags = [
            *(['-s'] if config.type == 'release' or config.type == 'size' else []),
            *(['-lstdc++exp'] if self.stdlib_name == 'libstdc++' else [])
        ]
        self.define_macros = {
            **({'DEBUG' : 'true'} if config.type == 'debug'   else 
               {'NDEBUG': 'true'} if config.type == 'release' else 
               {})
        }

    @syncable
    async def async_precompile(self, module_file, precompiled_file, object_file, compile_flags=[], define_macros={}, include_dirs=[], import_dirs=[], diagnostic_file=None):
        create_dir(parent_path(precompiled_file))
        create_dir(parent_path(object_file))
        await async_run(
            command=[
                self.path,
                *(self.compile_flags + compile_flags),
                *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
                *[f'-I{include_dir}' for include_dir in include_dirs],
                *[f'-fprebuilt-module-path={import_dir}' for import_dir in import_dirs],
                '--precompile', '-x', 'c++-module', module_file,
                '-o', precompiled_file
            ],
            log_command=(True, module_file),
        )
        await async_run(
            command=[
                self.path,
                *[f'-fprebuilt-module-path={import_dir}' for import_dir in import_dirs],
                '-c', module_file,
                '-o', object_file
            ]
        )

    @syncable
    async def async_compile(self, source_file, object_file, compile_flags=[], define_macros={}, include_dirs=[], import_dirs=[], diagnostic_file=None):
        create_dir(parent_path(object_file))
        await async_run(
            command=[
                self.path,
                *(self.compile_flags + compile_flags),
                *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
                *[f'-I{include_dir}' for include_dir in include_dirs],
                *[f'-fprebuilt-module-path={import_dir}' for import_dir in import_dirs],
                '-c', '-x', 'c++', source_file,
                '-o', object_file
            ],
            log_command=(True, source_file)
        )

    async def _async_get_version(self):
        return await Version.async_parse(
            name   =self.name,
            command=[self.path, '--version'],
            check  =lambda stdout: stdout.startswith('clang') or 'clang version' in stdout,
            lowest =21
        )

    async def _async_get_stdlib_name(self):
        stderr = await async_run(
            command=[
                self.path,
                *self.compile_flags,
                '-v',
            ],
            print_stderr=config.verbose,
            return_stderr=True
        )
        if 'selected gcc installation' in stderr.lower():
            return 'libstdc++'
        else:
            return 'libc++'    

    async def _async_get_stdlib_module_file(self):
        if self.stdlib_name == 'libc++':
            resource_dir = await async_run(
                command=[self.path, '--print-resource-dir'],
                return_stdout=True,
            )
            resource_dir = resource_dir.strip()
            module_file = f'{resource_dir}/../../../share/libc++/v1/std.cppm'
            if exist_file(module_file):
                return module_file
            else:
                raise ConfigError(f'libc++ module_file not found (with search_file = {module_file})')
        elif self.stdlib_name == 'libstdc++':
            return await Gcc._async_get_stdlib_module_file(self)
        else:
            assert False
