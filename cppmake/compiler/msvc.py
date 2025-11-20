from cppmake.error.config      import ConfigError
from cppmake.error.subprocess  import SubprocessError
from cppmake.execution.run     import async_run
from cppmake.utility.decorator import member, syncable

class Msvc:
    name          = "msvc"
    module_suffix = ".ixx"
    object_suffix = ".obj"
    def           __init__    (self, path="cl"):                                                                                       ...
    async def     __ainit__   (self, path="cl"):                                                                                       ...
    def             preprocess(self, code,                                                                                defines={}): ...
    async def async_preprocess(self, code,                                                                                defines={}): ...
    def             precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[],                defines={}): ...
    async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[],                defines={}): ...
    def             compile   (self, file, executable_file,          module_dirs=[], include_dirs=[], link_files=[], defines={}): ...
    async def async_compile   (self, file, executable_file,          module_dirs=[], include_dirs=[], link_files=[], defines={}): ...



@member(Msvc)
@syncable
async def __ainit__(self, path="cl"):
    await Msvc._async_check(path)
    self.path = path
    ...
    return self

@member(Msvc)
async def _async_check(path):
    try:
        version = await async_run(command=[path], return_stdout=True)
        if "msvc" not in version.lower():
            raise ConfigError(f'compiler is not msvc (with "{path} --version" outputs "{version.replace('\n', ' ')}")')
    except SubprocessError as error:
        raise ConfigError(f'compiler is not msvc (with "{path} --version" exits {error.code})')

    