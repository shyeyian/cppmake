from cppmakelib.basic.config          import config
from cppmakelib.basic.context         import context
from cppmakelib.error.config          import ConfigError
from cppmakelib.executor.operation    import when_all
from cppmakelib.executor.scheduler    import scheduler
from cppmakelib.logger.unit_status    import UnitStatusLogger
from cppmakelib.utility.decorator     import member, once, relocatable, syncable, trace, unique
from cppmakelib.utility.filesystem    import path, exist_dir
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
    # ========
    name               : str
    dir                : path
    # ========
    search_header_dir  : path # redefinable in cppmake.py
    search_module_dir  : path # redefinable in cppmake.py
    # ========
    build_dir          : path
    build_cache_dir    : path
    build_code_dir     : path
    build_header_dir   : path
    build_module_dir   : path
    build_source_dir   : path
    # ========
    install_dir        : path
    install_bin_dir    : path
    install_import_dir : path
    install_include_dir: path
    install_lib_dir    : path
    # ========
    compile_flags      : list[str]      # redefinable in cppmake.py
    link_flags         : list[str]      # redefinable in cppmake.py
    define_macros      : dict[str, str] # redefinable in cppmake.py
    # ========
    require_packages   : list[Package]
    # ========
    unit_status_logger : UnitStatusLogger
    # ========
    cppmake_file       : path
    cppmake            : types.ModuleType
    # ========
    

@member(Package)
@relocatable
@unique
@trace
def __init__(self: Package, dir: path) -> None:
    self.dir                 = dir
    self.search_header_dir   = f'{self.dir}/header'
    self.search_module_dir   = f'{self.dir}/module'
    self.build_dir           = f'binary/{config.type}/{self.name}/build'
    self.build_cache_dir     = f'{self.build_dir}/cache'
    self.build_code_dir      = f'{self.build_dir}/code'
    self.build_header_dir    = f'{self.build_dir}/header'
    self.build_module_dir    = f'{self.build_dir}/module'
    self.build_source_dir    = f'{self.build_dir}/source'
    self.install_dir         = f'binary/{config.type}/{self.name}/install'
    self.install_bin_dir     = f'{self.install_dir}/bin'
    self.install_import_dir  = f'{self.install_dir}/import'
    self.install_include_dir = f'{self.install_dir}/include'
    self.install_lib_dir     = f'{self.install_dir}/lib'
    self.compile_flags       = []
    self.link_flags          = []
    self.define_macros       = {}
    self.require_packages    = []
    self.unit_status_logger  = UnitStatusLogger(build_cache_dir=self.build_cache_dir)
    self.cppmake_file        = f'{self.dir}/cppmake.py'
    with context.switch(package=self):
        self.cppmake = import_module(file=self.cppmake_file, globals={'self': self})


@member(Package)
@syncable
@once
@trace
async def async_build(self: Package) -> None:
    await when_all([package.async_build() for package in self.require_packages])
    async with scheduler.schedule(scheduler.max):
        with context.switch(package=self):
            # lazy-print(f'build package {self.name}')
            self.cppmake.build() if hasattr(self.cppmake, 'build') else None
