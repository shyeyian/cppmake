from cppmakelib.basic.config      import config
from cppmakelib.basic.exit        import on_exit
from cppmakelib.builder.git       import git
from cppmakelib.compiler.all      import compiler
from cppmakelib.file.file_system  import create_dir, modified_time_of_file
from cppmakelib.system.all        import system
from cppmakelib.utility.decorator import member, syncable
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
        "time"           : time.time(),
        "config.compiler": config.compiler,
        "config.std"     : config.std,
        "git.log"        : await git.async_log   (git_dir) if git_dir is not None else None
    }

@member(PackageStatusLogger)
@syncable
async def async_get_status(self, name, git_dir, cppmake_file):
    return name in self._content.keys()                                                                         and \
           (cppmake_file is None or modified_time_of_file(cppmake_file) <= self._content[name]["time"])         and \
           config.std      == self._content[name]["config.std"]                                                 and \
           config.compiler == self._content[name]["config.compiler"]                                            and \
           (await git.async_log(git_dir) == self._content[name]["git.log"] if git_dir is not None else True)

package_status_logger = PackageStatusLogger()