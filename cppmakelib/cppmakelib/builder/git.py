from cppmakelib.execution.run     import async_run
from cppmakelib.utility.decorator import syncable, unique
from cppmakelib.utility.version   import Version

class Git:
    name = 'git'

    @syncable
    @unique
    async def __ainit__(self, path='git'):
        self.path    = path
        self.version = await self._async_get_version()

    @syncable
    async def async_log(self, git_dir):
        return await async_run(
            command=[
                self.path,
                '-C', git_dir,
                'log', '-1', '--format=%H'
            ],
            return_stdout=True
        )

    @syncable
    async def async_status(self, git_dir):
        return await async_run(
            command=[
                self.path,
                '-C', git_dir,
                'status', '--short'
            ],
            return_stdout=True
        )

    async def _async_get_version(self):
        return await Version.async_parse(
            name   =self.name, 
            command=[self.path, '--version'],
            check  =lambda stdout: stdout.startswith('git'),
            lowest =2
        )

git = Git()