from cppmakelib.unit.code import Code

class Module(Code):
    def           __new__         (cls: ..., file: path) -> Module     : ...
    async def    __anew__         (cls: ..., file: path) -> Module     : ...
    def           __init__        (self,     file: path) -> None       : ...
    async def    __ainit__        (self,     file: path) -> None       : ...
    def             precompile    (self)                 -> Precompiled: ...
    async def async_precompile    (self)                 -> Precompiled: ...
    def             is_precompiled(self)                 -> bool       : ...
    async def async_is_precompiled(self)                 -> bool       : ...
    name            : str
    precompiled_file: path
    object_file     : path
    diagnostic_file : path
    import_modules  : list[Module]



from cppmakelib.compiler.all       import compiler
from cppmakelib.executor.operation import when_all
from cppmakelib.executor.scheduler import scheduler
from cppmakelib.system.all         import system
from cppmakelib.unit.precompiled   import Precompiled
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, relocatable, syncable, unique
from cppmakelib.utility.filesystem import path

@member(Module)
@syncable
@unique
@relocatable
async def __ainit__(self: Module, file: path) -> None:
    await super(Module, self).__ainit__(file)
    self.name             = await self.context_package.unit_status_logger.async_get_module_name(module=self)
    self.precompiled_file = f'{self.context_package.build_import_dir}/{self.name.replace(':', '-')}{compiler.precompiled_suffix}'
    self.object_file      = f'{self.context_package.build_import_dir}/{self.name.replace(':', '-')}{system.object_suffix}'
    self.diagnostic_file  = f'{self.context_package.build_import_dir}/{self.name.replace(':', '.')}{compiler.diagnostic_suffix}'
    self.import_modules   = await when_all([Module.__anew__(Module, file) for file in await self.context_package.unit_status_logger.async_get_module_imports(module=self)])

@member(Module)
@syncable
@once
async def async_precompile(self: Module) -> Precompiled:
    if not await self.async_is_precompiled():
        await when_all([module.async_precompile() for module in self.import_modules])
        await self.async_preprocess()
        async with scheduler.schedule():
            print(f'precompile module {self.file}')
            await compiler.async_precompile(
                module_file     =self.file,
                precompiled_file=self.precompiled_file,
                object_file     =self.object_file,
                compile_flags   =self.compile_flags,
                define_macros   =self.define_macros,
                include_dirs    =[self.context_package.build_include_dir] + recursive_collect(self.context_package, next=lambda package: package.require_packages, collect=lambda package: package.install_include_dir),
                import_dirs     =[self.context_package.build_import_dir]  + recursive_collect(self.context_package, next=lambda package: package.require_packages, collect=lambda package: package.install_import_dir),
                diagnostic_file =self.diagnostic_file,
            )
        self.context_package.unit_status_logger.set_module_precompiled(module=self, precompiled=True)
    return Precompiled(self.precompiled_file)

@member(Module)
@syncable
@once
async def async_is_precompiled(self: Module) -> bool:
    return all(await when_all([module.async_is_precompiled() for module in self.import_modules ])) and \
           await self.async_is_preprocessed()                                                      and \
           self.context_package.unit_status_logger.get_module_precompiled(module=self)

