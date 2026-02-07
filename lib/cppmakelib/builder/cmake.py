class Cmake: 
    def           __init__(self, file: path = 'cmake')                                                                                   -> None: ...
    async def    __ainit__(self, file: path = 'cmake')                                                                                   -> None: ...
    def             build (self, package_dir: path, build_dir: path, install_dir: path, build_flags: list[str], prefix_dirs: list[path]) -> None: ...
    async def async_build (self, package_dir: path, build_dir: path, install_dir: path, build_flags: list[str], prefix_dirs: list[path]) -> None: ...
    file       : path
    version    : Version
    build_flags: list[str]

    async def _async_get_version(self) -> Version: ...

cmake: Cmake



from cppmakelib.basic.config       import config
from cppmakelib.compiler.all       import compiler
from cppmakelib.error.config       import ConfigError
from cppmakelib.error.subprocess   import SubprocessError
from cppmakelib.executor.run       import async_run
from cppmakelib.utility.decorator  import member, syncable
from cppmakelib.utility.filesystem import create_dir, path, remove_dir
from cppmakelib.utility.version    import Version

@member(Cmake)
@syncable
async def __ainit__(self: Cmake, file: path = 'cmake') -> None:
    self.file        = file
    self.version     = await self._async_get_version()
    self.build_flags = [
        f'-DCMAKE_BUILD_TYPE={config.type.capitalize()}',
        f'-DCMAKE_CXX_COMPILER={compiler.file}',
        f'-DCMAKE_CXX_FLAGS={compiler.compile_flags}'
    ]

@member(Cmake)
@syncable
async def async_build(
    self: Cmake, 
    package_dir: path,
    build_dir  : path,
    install_dir: path,
    build_flags: list[str], 
    prefix_dirs: list[path]
) -> None:
    try:
        create_dir(build_dir)
        await async_run(
            file=self.file,
            args=[
                *(self.build_flags + build_flags),
                f'-DCMAKE_INSTALL_PREFIX={install_dir}',
                f'-DCMAKE_PREFIX_PATH={';'.join(prefix_dirs)}',
                '-S', package_dir,
                '-B', build_dir,
            ]
        )
    except:
        remove_dir(build_dir)
        raise
    try:
        await async_run(
            file=self.file,
            args=[
                '--build', build_dir,
                '-j',      str(config.jobs)
            ]
        )
    except:
        raise
    try:
        create_dir(install_dir)
        await async_run(
            file=self.file,
            args=[
                '--install', build_dir,
                '-j',        str(config.jobs)
            ]
        )
    except:
        remove_dir(install_dir)
        raise

@member(Cmake)
async def _async_get_version(self: Cmake) -> Version:
    try:
        stdout = await async_run(
            file=self.file,
            args=['--version'],
            return_stdout=True
        )
    except SubprocessError as error:
        raise ConfigError(f'cmake check failed (with file = {self.file})') from error
    try:
        version = Version.parse(pattern=r'^cmake version (\d+)\.(\d+)\.(\d+)', string=stdout.splitlines()[0])
    except Version.ParseError as error:
        raise ConfigError(f'cmake check failed (with file = {self.file})') from error
    if version < 4:
        raise ConfigError(f'cmake version is too old (with file = {self.file}, version = {version}, requires = 4+)')
    return version

cmake = Cmake()