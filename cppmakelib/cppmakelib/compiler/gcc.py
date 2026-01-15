from cppmakelib.basic.config         import config
from cppmakelib.error.config         import ConfigError
from cppmakelib.execution.run        import async_run
from cppmakelib.file.file_system     import parent_path, exist_file, create_dir
from cppmakelib.logger.module_mapper import module_mapper_logger
from cppmakelib.system.all           import system
from cppmakelib.utility.decorator    import syncable, unique
from cppmakelib.utility.version      import Version
import re

class Gcc:
    name                = 'gcc'
    intermediate_suffix = '.i'
    precompiled_suffix  = '.gcm'

    @syncable
    @unique
    async def __ainit__(self, path='g++'):
        self.path               = path
        self.version            = await self._async_get_version()
        self.stdlib_name        = 'libstdc++'
        self.stdlib_module_file = await self._async_get_stdlib_module_file()
        self.stdlib_static_file = ...
        self.stdlib_shared_file = ...
        self.compile_flags = [
           f'-std={config.std}', '-fmodules', 
            *(['-O0', '-g'] if config.type == 'debug'   else
              ['-O3']       if config.type == 'release' else
              ['-Os']       if config.type == 'size'    else 
              []) 
        ]
        self.link_flags = [
           f'-fuse-ld={system.linker_path}',
            *(['-s'] if config.type == 'release' or config.type == 'size' else []),
            '-lstdc++exp'
        ]
        self.define_macros = {
            **({'DEBUG'  : 'true'} if config.type == 'debug'   else
               {'DNDEBUG': 'true'} if config.type == 'release' else
               {})
        }

    @syncable
    async def async_preprocess(self, unit_file, compile_flags=[], define_macros={}, include_dirs=[]):
        return await async_run(
            command=[
                self.path,
                *(self.compile_flags + compile_flags),
                *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
                *[f'-I{include_dir}' for include_dir in include_dirs],
                '-E', unit_file,
                '-o', '-'
            ],
            print_stdout=False,
            return_stdout=True
        )
    
    @syncable
    async def async_precompile(self, module_file, precompiled_file, object_file, compile_flags=[], define_macros={}, include_dirs=[], import_dirs=[], diagnostic_file=None):
        create_dir(parent_path(precompiled_file))
        create_dir(parent_path(object_file))
        create_dir(parent_path(diagnostic_file)) if diagnostic_file is not None else None
        await async_run(
            command=[
                self.path,
                *(self.compile_flags + compile_flags),
                *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
                *[f'-I{include_dir}' for include_dir in include_dirs],
                *[f'-fmodule-mapper={module_mapper_logger.get_mapper(import_dir)}' for import_dir in import_dirs],
                *([f'-fdiagnostics-add-output=sarif:code_file={diagnostic_file}'] if diagnostic_file is not None else []),
                '-c', '-x', 'c++-module', module_file,
                '-o', object_file
            ],
            log_command=(True, module_file)
        )
    
    @syncable
    async def async_compile(self, source_file, object_file, compile_flags=[], define_macros={}, include_dirs=[], import_dirs=[], diagnostic_file=None):
        create_dir(parent_path(object_file))
        create_dir(parent_path(diagnostic_file)) if diagnostic_file is not None else None
        await async_run(
            command=[
                self.path,
                *(self.compile_flags + compile_flags),
                *[f'-D{key}={value}' for key, value  in (self.define_macros | define_macros).items()],
                *[f'-I{include_dir}' for include_dir in include_dirs],
                *[f'-fmodule-mapper={module_mapper_logger.get_mapper(import_dir)}' for import_dir in import_dirs],
                *([f'-fdiagnostics-add-output=sarif:code_file={diagnostic_file}'] if diagnostic_file is not None else []),
                '-c', '-x', 'c++', source_file,
                '-o', object_file
            ],
            log_command=(True, source_file)
        )

    @syncable
    async def async_link(self, object_file, executable_file, link_flags=[], link_files=[]):
        create_dir(parent_path(executable_file))
        await async_run(
            command=[
                self.path,
                *(self.link_flags + link_flags),
                *([object_file] + link_files),
                '-o', executable_file
            ]
        )

    async def _async_get_version(self):
        return await Version.async_parse(
            name   =self.name
            command=[self.path, '--version'],
            check  =lambda stdout: stdout.startswith('g++'),
            lowest =15
        )

    async def _async_get_stdlib_module_file(self):
        stderr = await async_run(
            command=[
                self.path,
                *self.compile_flags,
                '-E', '-x', 'c++', '-'
                '-v' 
            ], 
            input_stdin='', 
            print_stderr=config.verbose, 
            return_stderr=True
        )
        search_dirs = re.search(r'^#include <...> search starts here:$\n(.*)\n^end of search list.$', stderr, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if search_dirs is None:
            raise ConfigError(f'libstdc++ module_file is not found (with "{self.path} -v -E -x c++ -" outputs "# invalid message")')
        search_dirs = [search_dir.strip() for search_dir in search_dirs.group(1).splitlines()]
        for include_dir in search_dirs:
            module_file = f'{include_dir}/bits/std.cc'
            if exist_file(module_file):
                return module_file
        else:
            raise ConfigError(f'libstdc++ module_file is not found (with search_file = {[f'{include_dir}/bits/std.cc' for include_dir in search_dirs]})')
