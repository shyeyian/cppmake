from cppmake.error.config      import ConfigError
from cppmake.error.subprocess  import SubprocessError
from cppmake.execution.run     import async_run
from cppmake.utility.decorator import member, syncable

class Git:
    name = "git"
    path = "git"
    def           __init__ (self):          ...
    async def     __ainit__(self):          ...
    def             log    (self, git_dir): ...
    async def async_log    (self, git_dir): ...
    def             status (self, git_dir): ...
    async def async_status (self, git_dir): ...

git = ...



@member(Git)
@syncable
async def __ainit__(self):
    await Git._async_check()

@member(Git)
@syncable
async def async_log(self, git_dir):
    return await async_run(
        command=[
            self.path,
            "-C", git_dir,
            "log", "-1", "--format=%H"
        ],
        return_stdout=True
    )

@member(Git)
@syncable
async def async_status(self, git_dir):
    return await async_run(
        command=[
            self.path,
            "-C", git_dir,
            "status", "--short"
        ],
        return_stdout=True
    )

@member(Git)
async def _async_check():
    try:
        version = await async_run(command=[Git.path, "--version"], return_stdout=True)
        if "git" not in version.lower():
            raise ConfigError(f'git is not installed (with "{Git.path} --version" outputs "{version.replace('\n', ' ')}")')
    except SubprocessError as error:
        raise ConfigError(f'git is not installed (with "{Git.path} --version" exits {error.code}')
        
git = Git()