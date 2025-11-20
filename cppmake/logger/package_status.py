from cppmake.basic.config      import config
from cppmake.basic.exit        import on_exit
from cppmake.builder.git       import git
from cppmake.file.file_system  import create_dir
from cppmake.system.all        import system
from cppmake.utility.decorator import member, syncable
import json
import time

class PackageStatusLogger:
    def           __init__    (self):          ...
    def           __exit__    (self):          ...
    def             log_status(self, package): ...
    async def async_log_status(self, package): ...
    def             get_status(self, package): ...
    async def async_get_status(self, package): ...

package_status_logger = ...


@member(PackageStatusLogger)
def __init__(self):
    create_dir(f"binary/{config.type}/cache")
    try:
        self._content = json.load(open(f"binary/{config.type}/cache/package_status.json", 'r'))
    except:
        self._content = {}
    on_exit(self.__exit__)
    
@member(PackageStatusLogger)
def __exit__(self):
    json.dump(self._content, open(f"binary/{config.type}/cache/package_status.json", 'w'), indent=4)

@member(PackageStatusLogger)
@syncable
async def async_log_status(self, name, git_dir):
    self._content[name] = {
        "time"      : time.time(),
        "env"       : dict(system.env),
        "compiler"  : config.compiler,
        "std"       : config.std,      
        "git_log"   : await git.async_log   (git_dir) if git_dir is not None else None,
        "git_status": await git.async_status(git_dir) if git_dir is not None else None
    }

@member(PackageStatusLogger)
@syncable
async def async_get_status(self, name, git_dir):
    return name in self._content.keys()                                                                                                   and \
           system.env      == self._content[name]["env"]                                                                                  and \
           config.compiler == self._content[name]["compiler"]                                                                             and \
           config.std      == self._content[name]["std"]                                                                                  and \
           (await git.async_log   (git_dir) == self._content[name]["git_log"]    if git_dir is not None else True) and \
           (await git.async_status(git_dir) == self._content[name]["git_status"] if git_dir is not None else True)



package_status_logger = PackageStatusLogger()