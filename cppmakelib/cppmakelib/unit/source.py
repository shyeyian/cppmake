from cppmakelib.compiler.all       import compiler
from cppmakelib.executor.operation import when_all
from cppmakelib.executor.scheduler import scheduler
from cppmakelib.system.all         import system
from cppmakelib.unit.code          import Code
from cppmakelib.unit.module        import Module
from cppmakelib.unit.object        import Object
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, relocatable, syncable, unique
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
@relocatable
@syncable
@unique
async def __ainit__(self: Source, file: path) -> None:
    await super(Source, self).__ainit__(file)
    self.object_file     = f'{self.context_package.build_source_dir}/{self.name}{system.object_suffix}'
    self.diagnostic_file = f'{self.context_package.build_source_dir}/{self.name}{system.executable_suffix}'
    self.import_modules  = await when_all([Module.__anew__(Module, file) for file in await self.context_package.unit_status_logger.async_get_source_imports(source=self)])

@member(Source)
@syncable
@once
async def async_compile(self: Source) -> Object:
    if not await self.async_is_compiled():
        await when_all([module.async_precompile() for module in self.import_modules ])
        await self.async_preprocess()
        async with scheduler.schedule():
            await compiler.async_compile(
                source_file    =self.file,
                object_file    =self.object_file,
                compile_flags  =self.compile_flags,
                define_macros  =self.define_macros,
                include_dirs   =[self.context_package.build_header_dir] + recursive_collect(self.context_package, next=lambda package: package.require_packages, collect=lambda package: package.install_include_dir, root=False),
                import_dirs    =[self.context_package.build_module_dir] + recursive_collect(self.context_package, next=lambda package: package.require_packages, collect=lambda package: package.install_import_dir,  root=False),                    
                diagnostic_file=self.diagnostic_file,
            )
        self.context_package.unit_status_logger.set_source_compiled(source=self, compiled=True)
    return Object(self.object_file)

@member(Source)
@syncable
@once
async def async_is_compiled(self: Source) -> bool:
    return all(await when_all([module.async_is_precompiled() for module in self.import_modules ])) and \
           await self.async_is_preprocessed()                                                      and \
           self.context_package.unit_status_logger.get_source_compiled(source=self)
