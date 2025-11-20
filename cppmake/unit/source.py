from cppmake.basic.config          import config
from cppmake.compiler.all          import compiler
from cppmake.error.logic           import LogicError
from cppmake.execution.operation   import when_all
from cppmake.execution.scheduler   import scheduler
from cppmake.file.file_system      import canonical_path, parent_path, exist_file, modified_time_of_file, iterate_dir
from cppmake.logger.module_imports import module_imports_logger
from cppmake.system.all            import system
from cppmake.unit.module           import Module
from cppmake.utility.algorithm     import recursive_collect
from cppmake.utility.decorator     import member, namable, once, syncable, trace, unique
from cppmake.utility.inline        import raise_

class Source:
    def           __new__       (cls,  name, file): ... # provide one of 'name' or 'file'
    async def     __anew__      (cls,  name, file): ... # provide one of 'name' or 'file'
    def           __init__      (self, name, file): ... # provide one of 'name' or 'file'
    async def     __ainit__     (self, name, file): ... # provide one of 'name' or 'file'
    def             compile     (self):             ...
    async def async_compile     (self):             ...
    def             is_compiled (self):             ...
    async def async_is_compiled (self):             ...



@member(Source)
@syncable
@namable
@unique
@once
@trace
async def __ainit__(self, name, file):
    self.name            = name
    self.file            = file
    self.executable_file = f"binary/{config.type}/source/{self.name.replace('.', '/')}{system.executable_suffix}"
    self.import_modules  = await when_all([Module.__anew__(Module, name) for name in await module_imports_logger.async_get_imports(type="source", file=self.file)])

@member(Source)
@syncable
@once
@trace
async def async_compile(self):
    if not await self.async_is_compiled():
        await when_all([module.async_precompile() for module in self.import_modules])
        async with scheduler.schedule():
            await compiler.async_compile(
                self.file,
                executable_file=self.executable_file,
                module_dirs    =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: parent_path(module.module_file),                             root=False),
                include_dirs   =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: module.import_package.include_dir,                           root=False),
                link_files     =recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: module.object_file,                                          root=False) + 
                                recursive_collect(self, next=lambda module: module.import_modules, collect=lambda module: iterate_dir(module.import_package.lib_dir, recursive=False), root=False, flatten=True),
                defines        =config.defines
            )

@member(Source)
@syncable
@once
@trace
async def async_is_compiled(self):
    return all(await when_all([module.async_is_precompiled() for module in self.import_modules])) and \
           exist_file(self.file)                                                                  and \
           exist_file(self.executable_file)                                                       and \
           modified_time_of_file(self.file) <= modified_time_of_file(self.executable_file)

@member(Source)
def _name_to_file(name):
    return f"source/{name.replace('.', '/')}.cpp"                                                                      if exist_file(f"source/{name.replace('.', '/')}.cpp") else \
           raise_(LogicError(f"source is not found (with name = {name}, file = source/{name.replace('.', '/')}.cpp)"))

@member(Source)
def _file_to_name(file):
    return canonical_path(file).removeprefix("source/").removesuffix(".cpp").replace('/', '.') if (canonical_path(file).startswith("source/") and canonical_path(file).endswith(".cpp")) and     exist_file(file) else \
           raise_(LogicError(f"source is not found (with file = {file})"))                     if (canonical_path(file).startswith("source/") and canonical_path(file).endswith(".cpp")) and not exist_file(file) else \
           raise_(LogicError(f'source does not match "source/**.cpp" (with file = {file})'))