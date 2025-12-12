from cppmakelib.basic.config          import config
from cppmakelib.error.logic           import LogicError
from cppmakelib.execution.operation   import when_all
from cppmakelib.execution.scheduler   import scheduler
from cppmakelib.file.file_import      import import_file
from cppmakelib.file.file_system      import canonical_path, exist_file, exist_dir, create_dir, iterate_dir
from cppmakelib.logger.package_status import package_status_logger
from cppmakelib.utility.algorithm     import recursive_collect
from cppmakelib.utility.decorator     import member, namable, once, syncable, trace, unique
from cppmakelib.utility.inline        import raise_

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
    self.build_dir       = f"binary/package/{self.name}/build"
    self.install_dir     = f"binary/package/{self.name}/install"
    self.include_dir     = f"binary/package/{self.name}/install/include"
    self.lib_dir         = f"binary/package/{self.name}/install/lib"
    self.export_modules  = ...
    self.import_packages = ...
    self.compile_flags   = []
    self.link_flags      = []
    self.define_macros   = {}
    self.cppmake         = import_file(self.cppmake_file, globals={"self": self}) if self.cppmake_file is not None else None

@member(Package)
@syncable
@once
@trace
async def async_build(self):
    if not await self.async_is_built():
        await when_all([package.async_build() for package in self.import_packages])
        async with scheduler.schedule(scheduler.max):
            print(f"build package: {self.name}")
            create_dir(self.build_dir)
            create_dir(self.install_dir)
            self.cppmake.build() if hasattr(self.cppmake, "build") else None
            await package_status_logger.async_log_status(package=self)

@member(Package)
@syncable
@once
@trace
async def async_is_built(self):
    from cppmakelib.unit.module import Module
    self.export_modules  = await when_all([Module.__anew__(Module, file=file) for file in iterate_dir(self.module_dir, recursive=True)])                                                                  if self.name != "main" else []
    self.import_packages = recursive_collect(self.export_modules, next=lambda module: module.import_modules, collect=lambda module: module.import_package if module.import_package is not self else None) if self.name != "main" else []
    return all(await when_all([package.async_is_built() for package in self.import_packages])) and \
           await package_status_logger.async_get_status(package=self)

@member(Package)
def _name_to_dir(name):
    return  '.'              if name == "main"               else \
           f"package/{name}" if exist_dir(f"package/{name}") else \
           raise_(LogicError(f"package is not found (with name = {name}, dir = package/{name})"))

@member(Package)
def _dir_to_name(dir):
    return "main"                                                                       if canonical_path(dir) == '.'                                        else \
           canonical_path(dir).remove_prefix("package/")                                if canonical_path(dir).startswith("package/") and     exist_dir(dir) else \
           raise_(LogicError(f"package is not found (with dir = {dir})"))               if canonical_path(dir).startswith("package/") and not exist_dir(dir) else \
           raise_(LogicError(f'package does not match "package/*" (with dir = {dir})'))