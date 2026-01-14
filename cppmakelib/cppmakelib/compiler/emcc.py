from cppmakelib.basic.config       import config
from cppmakelib.compiler.clang     import Clang
from cppmakelib.error.config       import ConfigError
from cppmakelib.error.subprocess   import SubprocessError
from cppmakelib.execution.run      import async_run
from cppmakelib.system.all         import system
from cppmakelib.utility.decorator  import syncable, unique
from cppmakelib.utility.version    import Version

class Emcc(Clang):
    name                = 'emcc'
    intermediate_suffix = '.i'
    preparsed_suffix    = '.pch'
    precompiled_suffix  = '.pcm'

    @syncable
    @unique
    async def __ainit__(self, path='em++'):
        self.path               = path
        self.version            = await self._async_get_version()
        self.stdlib_name        = 'libc++'
        self.stdlib_header_dir  = ...
        self.stdlib_module_file = await self._async_get_stdlib_module_file()
        self.stdlib_static_file = ...
        self.stdlib_shared_file = ...
        self.compile_flags = [
        f'-std={config.std}', '-fexceptions',
            *(['-O0', '-g'] if config.type == 'debug'   else
              ['-O3']       if config.type == 'release' else
              ['-Os']       if config.type == 'size'    else 
              [])
        ]
        self.link_flags = [
            *(['-s'] if config.type == 'release' or config.type == 'size' else []),
        ]
        self.define_macros = {
            **({'DEBUG' : 'true'} if config.type == 'debug'   else 
               {'NDEBUG': 'true'} if config.type == 'release' else 
               {})
        }

    @syncable
    async def async_link(self, object_file, executable_file, link_flags=[], link_files=[]):
        await Clang.async_link(
            self,
            object_file    =object_file,
            executable_file=executable_file - system.executable_suffix + '.js',
            link_flags     =link_flags,
            link_files     =link_files
        )

    async def _async_get_version(self):
        try:
            stdout = await async_run(command=[self.path, '--version'], return_stdout=True)
            if stdout.startswith('emcc'):
                version = Version.parse_from(stdout)
                if version >= 4:
                    return version
                else:
                    raise ConfigError(f'emcc is too old (with version = {version}, requires >= 4')
            else:
                raise ConfigError(f'emcc is not valid (with "{self.path} --version" returned "{stdout.replace('\n', ' ')}")')
        except SubprocessError as error:
            raise ConfigError(f'emcc is not valid (with "{self.path} --version" failed)') from error
        except FileNotFoundError as error:
            raise ConfigError(f'emcc is not found (with "{self.path}" not found)') from error
        
    async def _async_get_stdlib_module_file(self):
        stdlib_name = await Clang._async_get_stdlib_name(self)
        if stdlib_name == 'libc++':
            try:
                return await Clang._async_get_stdlib_module_file(self)
            except ConfigError as error:
                raise ConfigError(f'libc++ module_file not found (with compiler = {self.path}, subcompiler = clang++)') from error
        else:
            raise ConfigError(f'libc++ module_file not found (with compiler = {self.path}, subcompiler = clang++, stdlib_name = {stdlib_name})')
