from cppmakelib.basic.config      import config
from cppmakelib.compiler.all      import compiler
from cppmakelib.executor.run      import async_run
from cppmakelib.utility.filesystemimport path, create_dir, remove_dir
from cppmakelib.utility.algorithm import recursive_collect
from cppmakelib.utility.decorator import syncable, unique
from cppmakelib.utility.version   import Version

class Cmake:
    name: str = 'cmake'
    def       __init__ (self, path: path = path('cmake')) -> None: ...
    async def __ainit__(self, path: path = path('cmake')) -> None: ...
    def       async_build(self, package: Package, args: list[str]) -> None: ...



async def __ainit__(self, path: path = path('cmake')):
    self.path    = path
    self.version = await self._async_get_version()

@syncable
async def async_build(self, package, args):
    try:
        create_dir(package.build_dir)
        await async_run(
            command=[
                self.path,
                '-S', package.git_dir,
                '-B', package.build_dir,
                f'-DCMAKE_BUILD_TYPE={config.type}',
                f'-DCMAKE_CXX_COMPILER={compiler.path}',
                f'-DCMAKE_CXX_FLAGS={' '.join(compiler.compile_flags + package.compile_flags)}',
                f'-DCMAKE_PREFIX_PATH={';'.join(recursive_collect(package, next=lambda package: package.require_packages, collect=lambda package: package.install_dir, root=False))}',
                f'-DCMAKE_INSTALL_PREFIX={package.install_dir}',
                '-DCMAKE_INSTALL_LIBDIR=lib',
                *args
            ]
        )
    except:
        remove_dir(package.build_dir)
        raise
    try:
        await async_run(
            command=[
                self.path,
                '--build', package.build_dir,
                '-j',      str(config.parallel)
            ]
        )
    except:
        raise
    try:
        create_dir(package.install_dir)
        await async_run(
            command=[
                self.path,
                '--install', package.build_dir,
                '-j',        str(config.parallel)
            ]
        )
    except:
        remove_dir(package.install_dir)
        raise

async def _async_get_version(self):
    return await Version.async_parse(
        name   =self.name,
        command=[self.path, '--version'],
        check  =lambda stdout: stdout.startswith('cmake'),
        lowest =4
    )
