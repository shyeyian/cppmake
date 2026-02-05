from cppmakelib.basic.config       import config
from cppmakelib.compiler.all       import compiler
from cppmakelib.error.config       import ConfigError
from cppmakelib.error.subprocess   import SubprocessError
from cppmakelib.executor.run       import async_run
from cppmakelib.utility.filesystem import absolute_path, create_dir, path, remove_dir
from cppmakelib.utility.decorator  import member, syncable, unique
from cppmakelib.utility.version    import Version

class Makefile:
    def           __init__(self, file: path = 'make')                                                              -> None: ...
    async def    __ainit__(self, file: path = 'make')                                                              -> None: ...
    def             build (self, configure_file: path, build_dir: path, install_dir: path, build_flags: list[str]) -> None: ...
    async def async_build (self, configure_file: path, build_dir: path, install_dir: path, build_flags: list[str]) -> None: ...
    file       : path
    version    : Version
    build_flags: list[str]

    async def _async_get_version(self) -> Version: ...

makefile: Makefile



@member(Makefile)
@syncable
@unique
async def __ainit__(self: Makefile, file: path = 'make') -> None:
    self.file        = file
    self.version     = await self._async_get_version()
    self.build_flags = [
        f'CXX={compiler.file}',
        f'CXXFLAGS={compiler.compile_flags}'
    ]

@member(Makefile)
@syncable
async def async_build(
    self: Makefile, 
    configure_file: path,
    build_dir     : path, 
    install_dir   : path, 
    build_flags   : list[str], 
) -> None:
    try:
        create_dir(build_dir)
        await async_run(
            file=configure_file,
            args=[
                *(self.build_flags + build_flags),
                f'--prefix={absolute_path(install_dir)}',
            ],
            cwd=build_dir
        )
    except:
        remove_dir(build_dir)
        raise
    try:
        await async_run(
            file=self.file,
            args=[
                '-C', build_dir,
                '-j', str(config.parallel)
            ]
        )
    except:
        raise
    try:
        create_dir(install_dir)
        await async_run(
            file=self.file,
            args=[
                'install'
                '-C', build_dir,
                '-j', str(config.parallel)
            ]
        )
    except:
        remove_dir(install_dir)
        raise

@member(Makefile)
async def _async_get_version(self: Makefile) -> Version:
    try:
        stdout = await async_run(
            file=self.file,
            args=['--version'],
            return_stdout=True
        )
    except SubprocessError as error:
        raise ConfigError(f'makefile check failed (with file = {self.file})') from error
    try:
        version = Version.parse(pattern=r'^GNU Make (\d+\.\d+\.\d+)', string=stdout)
    except Version.ParseError as error:
        raise ConfigError(f'makefile check failed (with file = {self.file})') from error
    if version < 3:
        raise ConfigError(f'makefile version is too old (with file = {self.file}, version = {version}, requires = 3+)')
    return version
        
makefile = Makefile()