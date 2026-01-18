from cppmakelib.compiler.all           import compiler
from cppmakelib.execution.operation    import when_all
from cppmakelib.execution.scheduler    import scheduler
from cppmakelib.file.file_system       import parent_path
from cppmakelib.logger.source_status   import source_status_logger
from cppmakelib.logger.unit_preprocess import unit_preprocess_logger
from cppmakelib.system.all             import system
from cppmakelib.unit.module            import Module
from cppmakelib.unit.package           import Package
from cppmakelib.utility.algorithm      import recursive_collect
from cppmakelib.utility.decorator      import once, syncable, trace, unique

class Source:
    @syncable
    @unique
    @trace
    async def __ainit__(self, name):
        self.name            = name
        self.file            = f'source/{self.name}.cpp'
        self.object_file     = f'binary/source/{self.name}{compiler.object_suffix}'
        self.executable_file = f'binary/source/{self.name}{system.executable_suffix}'
        self.diagnostic_file = f'binary/.cache/{self.name}.sarif'
        self.depend_package  = await Package.__anew__(Package, '.')
        self.import_modules  = await when_all([Module.__anew__(Module, name) for name in await unit_preprocess_logger.async_query(unit=self).imports])
        self.compile_flags   = self.depend_package.compile_flags
        self.define_macros   = self.depend_package.define_macros
        self.link_flags      = self.depend_package.link_flags
    
    @syncable
    @once
    @trace
    async def async_compile(self):
        if not await self.async_is_compiled():
            await when_all([module.async_precompile() for module in self.import_modules])
            async with scheduler.schedule():
                print(f'compile source: {self.name}')
                await compiler.async_compile(
                    self.file,
                    object_file    =self.object_file,
                    executable_file=self.executable_file,
                    compile_flags  =self.compile_flags,
                    define_macros  =self.define_macros,
                    link_flags     =self.link_flags,
                    include_dirs   =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: module.depend_package.include_dir, root=False),
                    import_dirs    =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: parent_path(module.module_file),   root=False),                    
                    diagnostic_file=self.diagnostic_file,
                )
            source_status_logger.log(source=self)

    @syncable
    @once
    async def async_is_compiled(self):
        return all(await when_all([module.async_is_precompiled() for module in self.import_modules])) and \
               source_status_logger.query(source=self)
