from cppmakelib.basic.config       import config
from cppmakelib.compiler.all       import compiler
from cppmakelib.executor.operation import when_all
from cppmakelib.executor.scheduler import scheduler
from cppmakelib.logger.unit_status import unit_status_logger
from cppmakelib.system.all         import system
from cppmakelib.unit.code          import Code
from cppmakelib.unit.object        import Object
from cppmakelib.unit.precompiled   import Precompiled
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, syncable, trace, unique
from cppmakelib.utility.filesystem import path
import typing

class Module(Code):
    def           __init__        (self, file: path) -> None                      : ...
    async def    __ainit__        (self, file: path) -> None                      : ...
    def             precompile    (self)             -> tuple[Precompiled, Object]: ...
    async def async_precompile    (self)             -> tuple[Precompiled, Object]: ...
    def             is_precompiled(self)             -> bool                      : ...
    async def async_is_precompiled(self)             -> bool                      : ...
    name            : str
    precompiled_file: path
    object_file     : path
    diagnostic_file : path
    import_modules  : list[Module]

    if typing.TYPE_CHECKING:
        @staticmethod
        def           __new__(cls: type, file: path) -> Module: ...
        @staticmethod
        async def    __anew__(cls: type, file: path) -> Module: ...
    


@member(Module)
@syncable
@unique
@trace
async def __ainit__(self: Module, file: path) -> None:
    await super(Module, self).__ainit__(file)
    self.name             = unit_status_logger.get_module_name(file=self.file)
    self.precompiled_file = path()/'binary'/config.type/'module'/f'{self.name.replace(':', '-')}{compiler.precompiled_suffix}'
    self.object_file      = path()/'binary'/config.type/'module'/f'{self.name.replace(':', '-')}{system.object_suffix}'
    self.diagnostic_file  = path()/'binary'/  'cache'  /'module'/f'{self.name.replace(':', '.')}{compiler.diagnostic_suffix}'
    self.import_modules   = await when_all([Module.__anew__(Module, file) for file in unit_status_logger.get_module_imports(module=self)])

@member(Module)
@syncable
@once
@trace
async def async_precompile(self: Module) -> tuple[Precompiled, Object]:
    if not await self.async_is_precompiled():
        await when_all([module.async_precompile() for module in self.import_modules])
        await self.belong_package.async_build()
        await self.async_preprocess()
        async with scheduler.schedule():
            await compiler.async_precompile(
                module_file     =self.file,
                precompiled_file=self.precompiled_file,
                object_file     =self.object_file,
                diagnostic_file =self.diagnostic_file,
                compile_flags   =self.compile_flags,
                define_macros   =self.define_macros,
                include_dirs    =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: module.belong_package.include_dir),
                import_dirs     =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: module.parent_dir(file)),
            )
        unit_status_logger.set_module_precompiled(module=self, result=True)
    return Precompiled(self.precompiled_file), Object(self.object_file)

@member(Module)
@syncable
@once
async def async_is_precompiled(self: Module) -> bool:
    return all(await when_all([module.async_is_precompiled() for module in self.import_modules])) and \
           await self.belong_package.async_is_built()                                             and \
           await self.async_is_preprocessed()                                                     and \
           unit_status_logger.get_module_precompiled(module=self)

