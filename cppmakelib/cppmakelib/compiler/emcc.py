from cppmakelib.basic.config       import config
from cppmakelib.compiler.clang     import Clang
from cppmakelib.error.config       import ConfigError
from cppmakelib.error.subprocess   import SubprocessError
from cppmakelib.execution.run      import async_run
from cppmakelib.system.all         import _set_system
from cppmakelib.system.wasm        import Wasm
from cppmakelib.utility.decorator  import member, syncable
from cppmakelib.utility.version    import parse_version

class Emcc(Clang):
    name          = "emcc"
    module_suffix = ".pcm"
    object_suffix = ".o"
    def           __init__         (self, path="em++"): ...
    async def     __ainit__        (self, path="em++"): ...
    def             get_stdlib_file(self):              ...
    async def async_get_stdlib_file(self):              ...



@member(Emcc)
@syncable
async def __ainit__(self, path="em++"):
    self.path          = path
    self.version       = await self._async_get_version()
    self.stdlib_name   = "libc++"
    self.compile_flags = [
       f"-std={config.std}", "-fexceptions",
        *(["-O0", "-g"] if config.type == "debug"   else
          ["-O3",     ] if config.type == "release" else
          ["-Os"      ] if config.type == "size"    else 
          [])
    ]
    self.link_flags = [
        *(["-s"] if config.type == "release" or config.type == "size" else []),
    ]
    self.define_macros = {
        **({"DEBUG" : "true"} if config.type == "debug"   else 
           {"NDEBUG": "true"} if config.type == "release" else 
           {})
    }
    _set_system(Wasm())

@member(Emcc)
@syncable
async def async_get_version(self):
    try:
        version_str = await async_run(command=[self.path, "--version"], return_stdout=True)
        if version_str.startswith("emcc"):
            version = parse_version(version_str)
            if version >= 4:
                return version
            else:
                raise ConfigError(f'emcc is too old (with version = {version}, requires >= 4')
        else:
            raise ConfigError(f'emcc is not valid (with "{self.path} --version" outputs "{version_str.replace('\n', ' ')}")')
    except SubprocessError as error:
        raise ConfigError(f'emcc is not valid (with "{self.path} --version" outputs "{error.stderr.replace('\n', ' ')}" and exits {error.code})')
    except FileNotFoundError as error:
        raise ConfigError(f'emcc is not found (with "{self.path} --version" fails "{error}")')
    
@member(Emcc)
@syncable
async def async_get_stdlib_file(self):
    clang = Clang()
    if clang.stdlib_name == self.stdlib_name:
        try:
            return await clang.async_get_stdlib_file()
        except ConfigError as error:
            raise ConfigError(f"libc++ module not found (with compiler = {self.path}, subcompiler = clang++), because\n  {error}")
    else:
        raise ConfigError(f"libc++ module not found (with compiler = {self.path}, subcompiler = clang++, stdlib_name = {clang.stdlib_name})")