from cppmakelib.error.config      import ConfigError
from cppmakelib.error.subprocess  import SubprocessError
from cppmakelib.execution.run     import async_run
from cppmakelib.utility.decorator import member, syncable

class Msvc:
    name          = "msvc"
    module_suffix = ".ixx"
    object_suffix = ".obj"
    def           __init__    (self, path="cl"):                                                                                           ...
    async def     __ainit__   (self, path="cl"):                                                                                           ...
    def             preprocess(self, code,                                                            compile_flags=[], define_macros={}): ...
    async def async_preprocess(self, code,                                                            compile_flags=[], define_macros={}): ...
    def             precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}): ...
    async def async_precompile(self, file, module_file, object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}): ...
    def             compile   (self, file,              object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}): ...
    async def async_compile   (self, file,              object_file, module_dirs=[], include_dirs=[], compile_flags=[], define_macros={}): ...
    def             link      (self, file, executable_file,                          link_files  =[], link_flags   =[]                  ): ...
    async def async_link      (self, file, executable_file,                          link_files  =[], link_flags   =[]                  ): ...




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
            raise ConfigError(f'msvc is not valid (with "{path}" outputs "{version.replace('\n', ' ')}")')
    except SubprocessError as error:
        raise ConfigError(f'msvc is not valid (with "{path}" outputs "{error.stderr.replace('\n', ' ')}" and exits {error.code})')
    except FileNotFoundError as error:
        raise ConfigError(f'msvc is not found (with "{path}" fails "{error}")')

    