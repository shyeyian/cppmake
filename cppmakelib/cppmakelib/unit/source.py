from cppmakelib.basic.config       import config
from cppmakelib.compiler.all       import compiler
from cppmakelib.executor.operation import when_all
from cppmakelib.executor.scheduler import scheduler
from cppmakelib.logger.unit_status import unit_status_logger
from cppmakelib.system.all         import system
from cppmakelib.unit.code          import Code
from cppmakelib.unit.module        import Module
from cppmakelib.unit.object        import Object
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, syncable, trace, unique
from cppmakelib.utility.filesystem import path
import typing

class Source(Code):
    def           __init__     (self, file: path) -> None  : ...
    async def    __ainit__     (self, file: path) -> None  : ...
    def             compile    (self)             -> Object: ...
    async def async_compile    (self)             -> Object: ...
    def             is_compiled(self)             -> bool  : ...
    async def async_is_compiled(self)             -> bool  : ...
    name           : str
    object_file    : path
    diagnostic_file: path
    import_modules : list[Module]

    if typing.TYPE_CHECKING:
        @staticmethod
        def           __new__(cls: type, file: path) -> Source: ...
        @staticmethod
        async def    __anew__(cls: type, file: path) -> Source: ...



@member(Source)
@syncable
@unique
@trace
async def __ainit__(self: Source, file: path) -> None:
    await super(Source, self).__ainit__(file)
    self.name            = self.file.relative_path(from_path=self.belong_package.source_dir).removesuffix('.cpp')
    self.object_file     = path()/'binary'/config.type/'source'/f'{self.name}{system.object_suffix}'
    self.diagnostic_file = path()/'binary'/  'cache'  /'source'/f'{self.name}{system.executable_suffix}'
    self.import_modules  = await when_all([Module.__anew__(Module, file) for file in unit_status_logger.get_source_imports(source=self)])

@member(Source)
@syncable
@once
@trace
async def async_compile(self: Source) -> Object:
    if not await self.async_is_compiled():
        await when_all([module.async_precompile() for module in self.import_modules])
        await self.belong_package.async_is_built()
        await self.async_preprocess()
        async with scheduler.schedule():
            await compiler.async_compile(
                source_file    =self.file,
                object_file    =self.object_file,
                compile_flags  =self.compile_flags,
                define_macros  =self.define_macros,
                include_dirs   =recursive_collect(self, next=lambda code: code.import_modules, collect=lambda module: module.belong_package.include_dir, root=False),
                import_dirs    =recursive_collect(self, next=lambda code: code.import_modules, collect=lambda module: module.parent_dir(file),         root=False),                    
                diagnostic_file=self.diagnostic_file,
            )
        unit_status_logger.set_source_compiled(source=self, result=True)
    return Object(self.object_file)

@member(Source)
@syncable
@once
async def async_is_compiled(self: Source) -> bool:
    return all(await when_all([module.async_is_precompiled() for module in self.import_modules])) and \
           await self.belong_package.async_is_built()                                             and \
           await self.async_is_preprocessed()                                                     and \
           unit_status_logger.get_source_compiled(source=self)
