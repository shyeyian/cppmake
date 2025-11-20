from cppmake.basic.config          import config
from cppmake.error.logic           import LogicError
from cppmake.execution.operation   import when_all
from cppmake.execution.scheduler   import scheduler
from cppmake.file.file_import      import import_file
from cppmake.file.file_system      import canonical_path, exist_file, exist_dir, iterate_dir
from cppmake.logger.package_status import package_status_logger
from cppmake.utility.algorithm     import recursive_collect
from cppmake.utility.decorator     import member, namable, once, syncable, trace, unique
from cppmake.utility.inline        import raise_

class Package:
    def           __new__   (cls,  name, dir): ... # provide one of 'name' or 'dir'.
    async def     __anew__  (cls,  name, dir): ... # previde one of 'name' or 'dir'.
    def           __init__  (self, name, dir): ... # provide one of 'name' or 'dir'.
    async def     __ainit__ (self, name, dir): ... # provide one of 'name' or 'dir'.
    def             build   (self):            ...
    async def async_build   (self):            ...
    def             is_built(self):            ...
    async def async_is_built(self):            ...



@member(Package)
@syncable
@namable
@unique
@once
@trace
async def __ainit__(self, name, dir):
    self.name            = name
    self.dir             = dir
    self.git_dir         = f"{self.dir}/git"        if exist_dir (f"{self.dir}/git")        else None
    self.module_dir      = f"{self.dir}/module"     if exist_dir (f"{self.dir}/module")     else raise_(LogicError(f"package does not have a module_dir (with name = {self.name}, module_dir = {self.dir}/module)"))
    self.cppmake_file    = f"{self.dir}/cppmake.py" if exist_file(f"{self.dir}/cppmake.py") else None
    self.build_dir       = f"binary/{config.type}/package/{self.name}/build"
    self.install_dir     = f"binary/{config.type}/package/{self.name}/install"
    self.include_dir     = f"binary/{config.type}/package/{self.name}/install/include"
    self.lib_dir         = f"binary/{config.type}/package/{self.name}/install/lib"
    self.cppmake         = import_file(self.cppmake_file)
    self.defines         = self.cppmake.defines
    self.modules         = ...
    self.import_packages = ...

@member(Package)
@syncable
@once
@trace
async def async_build(self):
    if not await self.async_is_built():
        await when_all([package.async_build() for package in self.import_packages])
        async with scheduler.schedule(scheduler.max):
            self.cppmake.build()
            await package_status_logger.async_log_status(name=self.name, git_dir=self.git_dir)

@member(Package)
@syncable
@once
@trace
async def async_is_built(self):
    from cppmake.unit.module import Module
    self.modules = await when_all([Module.__anew__(Module, file=file) for file in iterate_dir(self.module_dir, recursive=True)])
    self.import_packages = recursive_collect(self.modules, next=lambda module: module.import_modules, collect=lambda module: module.import_package if module.import_package is not self else None)
    print(f"package {self.name} imports {[package.name for package in self.import_packages]}")
    return all(await when_all([package.async_is_built() for package in self.import_packages])) and \
           exist_dir(self.install_dir)                                                         and \
           await package_status_logger.async_get_status(name=self.name, git_dir=self.git_dir)

@member(Package)
def _name_to_dir(name):
    return f"package/{name}" if exist_dir(f"package/{name}") else \
           raise_(LogicError(f"package is not found (with name = {name}, dir = package/{name})"))

@member(Package)
def _dir_to_name(dir):
    return canonical_path(dir).remove_prefix("package/")                                if canonical_path(dir).startswith("package/") and     exist_dir(dir) else \
           raise_(LogicError(f"package is not found (with dir = {dir})"))               if canonical_path(dir).startswith("package/") and not exist_dir(dir) else \
           raise_(LogicError(f'package does not match "package/*" (with dir = {dir})'))