from cppmakelib.basic.context      import context
from cppmakelib.unit.package       import Package
from cppmakelib.utility.decorator  import member, unique
from cppmakelib.utility.filesystem import modified_time_file, path
from cppmakelib.utility.time       import time

class Binary:
    def           __new__  (cls,  file       : path) -> Binary: ...
    def           __init__ (self, file       : path) -> None  : ...
    def             install(self, install_dir: path) -> Binary: ...
    async def async_install(self, install_dir: path) -> Binary: ...
    def             sign   (self)                    -> Binary: ...
    async def async_sign   (self)                    -> Binary: ...
    def             strip  (self)                    -> Binary: ...
    async def async_strip  (self)                    -> Binary: ...
    file           : path
    modified_time  : time
    context_package: Package
    link_flags     : list[str]



@member(Binary)
@unique
def __init__(self: Binary, file: path) -> None:
    self.file            = file
    self.modified_time   = modified_time_file(self.file)
    self.context_package = context.package
    self.link_flags      = self.context_package.link_flags