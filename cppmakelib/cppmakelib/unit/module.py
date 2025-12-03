from cppmakelib.basic.config           import config
from cppmakelib.compiler.all           import compiler
from cppmakelib.error.logic            import LogicError
from cppmakelib.execution.operation    import when_all
from cppmakelib.execution.scheduler    import scheduler
from cppmakelib.file.file_system       import parent_path, canonical_path, exist_file, exist_dir, modified_time_of_file
from cppmakelib.logger.module_mapper   import module_mapper_logger
from cppmakelib.logger.module_status   import module_status_logger
from cppmakelib.logger.unit_preprocess import unit_preprocess_logger
from cppmakelib.unit.package           import Package
from cppmakelib.utility.algorithm      import recursive_collect
from cppmakelib.utility.decorator      import member, namable, once, syncable, trace, unique
from cppmakelib.utility.inline         import raise_
import re

class Module:
    def           __new__         (cls,  name, file): ... # provide one of 'name' or 'file'.
    async def     __anew__        (cls,  name, file): ... # previde one of 'name' or 'file'.
    def           __init__        (self, name, file): ... # provide one of 'name' or 'file'.
    async def     __ainit__       (self, name, file): ... # provide one of 'name' or 'file'.
    def             precompile    (self):             ...
    async def async_precompile    (self):             ... 
    def             is_precompiled(self):             ...
    async def async_is_precompiled(self):             ...



@member(Module)
@syncable
@namable
@unique
@once
@trace
async def __ainit__(self, name, file):
    self.name           = name
    self.file           = file
    self.module_file    = f"binary/module/{self.name.replace(':', '-')}{compiler.module_suffix}"
    self.object_file    = f"binary/module/{self.name.replace(':', '-')}{compiler.object_suffix}"
    self.diagnose_file  = f"binary/cache/module.{self.name.replace(':', '.')}.sarif"
    self.optimize_file  = f"binary/cache/module.{self.name.replace(':', '.')}.optim"
    self.import_package = await Package.__anew__(Package, "main" if self.file.startswith("module/") else self.name.split(':')[0].split('.')[0])
    self.import_modules = await when_all([Module.__anew__(Module, import_) for import_ in await unit_preprocess_logger.async_get_imports(unit=self)])
    self.compile_flags  = self.import_package.compile_flags
    self.define_macros  = self.import_package.define_macros
    module_mapper_logger.log_mapper(name=self.name, module_file=self.module_file)

@member(Module)
@syncable
@once
@trace
async def async_precompile(self):
    if not await self.async_is_precompiled():
        await when_all([module.async_precompile() for module in self.import_modules])
        await self.import_package.async_build() if self.import_package is not None else None
        async with scheduler.schedule():
            print(f"precompile module: {self.name}")
            await compiler.async_precompile(
                self.file,
                module_file  =self.module_file,
                object_file  =self.object_file,
                module_dirs  =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: parent_path(module.module_file)),
                include_dirs =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: module.import_package.include_dir),
                compile_flags=self.compile_flags,
                define_macros=self.define_macros,
                diagnose_file=self.diagnose_file,
                optimize_file=self.optimize_file
            )
            module_status_logger.log_status(module=self)

@member(Module)
@syncable
@once
@trace
async def async_is_precompiled(self):
    return all(await when_all([module.async_is_precompiled() for module in self.import_modules]))    and \
           (await self.import_package.async_is_built() if self.import_package is not None else True) and \
           module_status_logger.get_status(module=self)

@member(Module)
def _name_to_file(name):
    main_path =                                            f"module/{name.replace('.', '/').replace(':', '/')}.cpp"
    pack_path = f"package/{name.split(':')[0].split('.')[0]}/module/{name.replace('.', '/').replace(':', '/')}.cpp"
    return main_path                                                                                                if     exist_file(main_path) and not exist_file(pack_path) else \
           pack_path                                                                                                if not exist_file(main_path) and     exist_file(pack_path) else \
           raise_(LogicError(f"module is not found (with name = {name}, path = {{{main_path}, {pack_path}}})"))     if not exist_file(main_path) and not exist_file(pack_path) else \
           raise_(LogicError(f"module is ambiguous (with name = {name}, path = {{{main_path}, {pack_path}}})"))

@member(Module)
async def _async_file_to_name(file):
    return await unit_preprocess_logger.async_get_export(file=canonical_path(file))                                       if re.match(r'^(package/\w+/)?module/.*\.cpp$', canonical_path(file)) and     exist_file(file) else \
           raise_(LogicError(f"module is not found (with file = {file})"))                                                if re.match(r'^(package/\w+/)?module/.*\.cpp$', canonical_path(file)) and not exist_file(file) else \
           raise_(LogicError(f'module does not match "module/**.cpp" or "package/*/module/**.cpp" (with file = {file})'))
