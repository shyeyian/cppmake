from cppmakelib.basic.config       import config
from cppmakelib.compiler.clang     import Clang
from cppmakelib.error.config       import ConfigError
from cppmakelib.utility.decorator  import syncable, unique
from cppmakelib.utility.version    import Version

class Emcc(Clang):
    name                = 'emcc'
    intermediate_suffix = '.i'
    precompiled_suffix  = '.pcm'

    @syncable
    @unique
    async def __ainit__(self, path='em++'):
        self.path               = path
        self.version            = await self._async_get_version()
        self.stdlib_name        = 'libc++'
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
                                      
    async def _async_get_version(self):
        return await Version.async_parse(
            name   =self.name,
            command=[self.path, '--version'],
            check  =lambda stdout: stdout.startswith('em++'),
            lowest =4
        )
        
    async def _async_get_stdlib_module_file(self):
        stdlib_name = await Clang._async_get_stdlib_name(self)
        if stdlib_name == 'libc++':
            try:
                return await Clang._async_get_stdlib_module_file(self)
            except ConfigError as error:
                raise ConfigError(f'libc++ module_file not found (with compiler = {self.path}, subcompiler = clang++)') from error
        else:
            raise ConfigError(f'libc++ module_file not found (with compiler = {self.path}, subcompiler = clang++, stdlib_name = {stdlib_name})')
