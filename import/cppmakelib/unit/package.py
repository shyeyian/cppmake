class Package:
    def           __new__   (cls,  name: str) -> Package: ...
    def           __init__  (self, name: str) -> None   : ...
    def             build   (self)            -> None   : ...
    async def async_build   (self)            -> None   : ...
    def             is_built(self)            -> bool   : ...
    async def async_is_built(self)            -> bool   : ...
    # ========
    name               : str
    dir                : path
    # ========
    include_dir        : path # redefinable in cppmake.py
    import_dir         : path # redefinable in cppmake.py
    # ========
    build_dir          : path
    build_include_dir  : path
    build_import_dir   : path
    build_utility_dir  : path
    install_dir        : path
    install_include_dir: path
    install_import_dir : path
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



from cppmakelib.basic.config       import config
from cppmakelib.executor.operation import when_all
from cppmakelib.executor.scheduler import scheduler
from cppmakelib.logger.unit_status import UnitStatusLogger
from cppmakelib.utility.decorator  import member, once, syncable, unique
from cppmakelib.utility.filesystem import path
from cppmakelib.utility.import_    import import_module
import types

@member(Package)
@unique
def __init__(self: Package, name: str) -> None:
    self.name                = name
    self.dir                 = '.'                           if self.name == 'main' else f'pkg/{self.name}'
    self.include_dir         = f'{self.dir}/include'
    self.import_dir          = f'{self.dir}/import'
    self.build_dir           = f'.cppmake/{config.type}'     if self.name == 'main' else f'.cppmake/{config.type}/pkg/{self.name}/build'
    self.build_include_dir   = f'{self.build_dir}/include'
    self.build_import_dir    = f'{self.build_dir}/import'
    self.build_utility_dir   = f'{self.build_dir}/utility'
    self.install_dir         = f'.cppmake/{config.type}'     if self.name == 'main' else f'.cppmake/{config.type}/pkg/{self.name}/install'
    self.install_include_dir = f'{self.install_dir}/include'
    self.install_import_dir  = f'{self.install_dir}/import'
    self.compile_flags       = []
    self.link_flags          = []
    self.define_macros       = {}
    self.require_packages    = []
    self.unit_status_logger  = UnitStatusLogger(build_utility_dir=self.build_utility_dir)
    self.cppmake_file        = f'{self.dir}/cppmake.py'
    if self.name != 'main':
        from cppmakelib.basic.context import context
        with context.switch(package=self):
            self.cppmake = import_module(file=self.cppmake_file, globals={'self': self})


@member(Package)
@syncable
@once
async def async_build(self: Package) -> None:
    from cppmakelib.basic.context import context
    await when_all([package.async_build() for package in self.require_packages])
    async with scheduler.schedule(scheduler.max):
        with context.switch(package=self):
            print(f'build package {self.name}')
            self.cppmake.build() if hasattr(self.cppmake, 'build') else None

