from cppmakelib.basic.config           import config
from cppmakelib.compiler.all           import compiler
from cppmakelib.error.config           import ConfigError
from cppmakelib.execution.operation    import when_all
from cppmakelib.execution.scheduler    import scheduler
from cppmakelib.file.file_system       import parent_path, exist_file
from cppmakelib.logger.module_status   import module_status_logger
from cppmakelib.logger.unit_preprocess import unit_preprocess_logger
from cppmakelib.unit.package           import Package
from cppmakelib.utility.algorithm      import recursive_collect
from cppmakelib.utility.decorator      import once, syncable, trace, unique

class Module:
    @syncable
    @unique
    @trace
    async def __ainit__(self, name):
        self.name             = name
        self.file             = Module._search(name)
        self.precompiled_file = 'binary/module/{self.name.replace(':', '-')}{compiler.module_suffix}'
        self.object_file      = f'binary/module/{self.name.replace(':', '-')}{compiler.object_suffix}'
        self.diagnostic_file  = f'binary/.cache/module.{self.name.replace(':', '.')}.sarif'
        self.depend_package   = Package._search(name)
        self.import_modules   = await when_all([Module.__anew__(Module, name) for name in await unit_preprocess_logger.async_query(unit=self).imports])
        self.compile_flags    = self.depend_package.compile_flags
        self.define_macros    = self.depend_package.define_macros

    @syncable
    @once
    @trace
    async def async_precompile(self):
        if not await self.async_is_precompiled():
            await when_all([module.async_precompile() for module in self.import_modules])
            await self.depend_package.async_build()
            async with scheduler.schedule():
                print(f'precompile module: {self.name}')
                await compiler.async_precompile(
                    module_file     =self.file,
                    precompiled_file=self.precompiled_file,
                    object_file     =self.object_file,
                    diagnostic_file =self.diagnostic_file,
                    compile_flags   =self.compile_flags,
                    define_macros   =self.define_macros,
                    include_dirs    =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: module.depend_package.include_dir),
                    import_dirs     =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: parent_path(module.module_file)),
                )
            module_status_logger.async_log(module=self)

    @syncable
    @once
    async def async_is_precompiled(self):
        return all(await when_all([module.async_is_precompiled() for module in self.import_modules])) and \
               await self.depend_package.async_is_built()                                             and \
               module_status_logger.query(module=self)
    
    def _search(name):
        candidates =         [f'{search_dir}/{name.replace('.', '/').replace(':', '/')}' for search_dir in config.module_search_dirs] + \
                     [f'{package.module_dir}/{name.replace('.', '/').replace(':', '/')}' for package    in Package._pool]
        candidates = [candidate for candidate in candidates if exist_file(candidate)]
        if len(candidates) == 0:
            raise ConfigError(f'module {name} is not found (with module_search_dirs = {config.module_search_dirs + [package.module_dir for package in Package._pool]})')
        elif len(candidates) == 1:
            return candidates[0]
        else:
            raise ConfigError(f'module {name} is ambiguous (with candidates = {candidates})')
