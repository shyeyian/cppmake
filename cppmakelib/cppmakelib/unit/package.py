from cppmakelib.basic.config          import config
from cppmakelib.error.config          import ConfigError
from cppmakelib.executor.operation    import when_all
from cppmakelib.executor.scheduler    import scheduler
from cppmakelib.logger.unit_status    import unit_status_logger
from cppmakelib.utility.decorator     import member, once, syncable, trace, unique
from cppmakelib.utility.filesystem    import path, exist_dir, exist_file
from cppmakelib.utility.module        import import_module
import types
import typing

class Package:
    def           __new__   (cls,  dir: path) -> Package: ...
    def           __init__  (self, dir: path) -> None   : ...
    def             build   (self)            -> None   : ...
    async def async_build   (self)            -> None   : ...
    def             is_built(self)            -> bool   : ...
    async def async_is_built(self)            -> bool   : ...
    name           : str
    dir            : path
    header_dir     : path
    module_dir     : path
    source_dir     : path
    cppmake_file   : path
    build_dir      : path
    install_dir    : path
    include_dir    : path
    import_dir     : path
    lib_dir        : path
    depend_packages: list[Package]
    compile_flags  : list[str]
    link_flags     : list[str]
    define_macros  : dict[str, str]
    cppmake        : types.ModuleType | None

    @staticmethod
    def _get_name(dir: path) -> str: ...
    @staticmethod
    def _which_contains(file: path) -> Package: ...
    
    

@member(Package)
@unique
@trace
def __init__(self: Package, dir: path) -> None:
    self.name             = Package._get_name(dir)
    self.dir              = dir
    self.header_dir       = self.dir/'header'
    self.module_dir       = self.dir/'module'
    self.source_dir       = self.dir/'source'
    self.cppmake_file     = self.dir/'cppmake.py'
    self.build_dir        = path()/'binary'/config.type/'package'/self.name/'build'
    self.install_dir      = path()/'binary'/config.type/'package'/self.name/'install'
    self.include_dir      = path()/'binary'/config.type/'package'/self.name/'install'/'include'
    self.import_dir       = path()/'binary'/config.type/'package'/self.name/'install'/'import'
    self.lib_dir          = path()/'binary'/config.type/'package'/self.name/'install'/'lib'
    self.depend_packages  = [] # defined in cppmake.py
    self.compile_flags    = [] # defined in cppmake.py
    self.link_flags       = [] # defined in cppmake.py
    self.define_macros    = {} # defined in cppmake.py
    with context.switch(build_dir=self.build_dir, )
    self.cppmake          = import_module(self.cppmake_file, globals={'self': self}) if exist_file(self.cppmake_file) else None

@member(Package)
@syncable
@once
@trace
async def async_build(self: Package) -> None:
    if not await self.async_is_built():
        await when_all([package.async_build() for package in self.depend_packages])
        async with scheduler.schedule(scheduler.max):
            self.cppmake.build() if self.cppmake is not None and hasattr(self.cppmake, 'build') else None
        unit_status_logger.set_package_built(package=self, result=True)

@member(Package)
@syncable
@once
async def async_is_built(self: Package) -> bool:
    return all(await when_all([package.async_is_built() for package in self.depend_packages])) and \
           unit_status_logger.get_package_built(package=self)

@member(Package)
def _search(name: str) -> path:
    if name == 'main':
        return path()
    elif exist_dir(path()/'package'/'name'):
        return path()/'package'/'name'
    else:
        raise ConfigError(f'package {name} is not found')
