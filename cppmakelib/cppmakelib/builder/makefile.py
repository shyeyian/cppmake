from cppmakelib.basic.config      import config
from cppmakelib.compiler.all      import compiler
from cppmakelib.execution.run     import async_run
from cppmakelib.file.file_system  import absolute_path, create_dir, remove_dir
from cppmakelib.utility.decorator import syncable, unique
from cppmakelib.utility.version   import Version

class Makefile:
    name = 'makefile'

    @syncable
    @unique
    async def __ainit__(self, path='make'):
        self.path    = path
        self.version = await self.async_get_version()

    @syncable
    async def async_build(self, package, file='configure', args=[]):
        try:
            create_dir(package.build_dir)
            await async_run(
                command=[
                   f'{package.git_dir}/{file}',
                   f'CXX={compiler.path}',
                   f'CXXFLAGS={' '.join(compiler.compile_flags + package.compile_flags)}'
                   f'--prefix={absolute_path(package.install_dir)}',
                   f'--libdir={absolute_path(package.install_dir)}/lib'
                    *args
                ],
                cwd=package.build_dir
            )
        except:
            remove_dir(package.build_dir)
            raise
        try:
            await async_run(
                command=[
                    self.path,
                   f'CXX={compiler.path}',
                   f'CXXFLAGS={' '.join(compiler.compile_flags + package.compile_flags)}'
                    '-C', package.build_dir,
                    '-j', str(config.parallel)
                ]
            )
        except:
            raise
        try:
            create_dir(package.install_dir)
            await async_run(
                command=[
                    self.path, 'install'
                    '-C', package.build_dir,
                    '-j', str(config.parallel)
                ]
            )
        except:
            remove_dir(package.install_dir)
            raise

    async def _async_get_version(self):
        return await Version.async_parse(
            name   ='makefile',
            command=[self.path, '--version'],
            check  =lambda stdout: stdout.startswith('GNU Make'),
            lowest =4
        )
            
makefile = Makefile()