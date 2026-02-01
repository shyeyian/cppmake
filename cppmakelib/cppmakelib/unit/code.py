from cppmakelib.basic.context      import context
from cppmakelib.compiler.all       import compiler
from cppmakelib.executor.scheduler import scheduler
from cppmakelib.unit.package       import Package
from cppmakelib.unit.preprocessed  import Preprocessed
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, relocatable, syncable, unique
from cppmakelib.utility.filesystem import modified_time_file, path, relative_path
from cppmakelib.utility.time       import time

class Code:
    def           __new__          (cls: ..., file: path) -> Code        : ...
    async def    __anew__          (cls: ..., file: path) -> Code        : ...
    def           __init__         (self,     file: path) -> None        : ...
    async def    __ainit__         (self,     file: path) -> None        : ...
    def             preprocess     (self)                 -> Preprocessed: ...
    async def async_preprocess     (self)                 -> Preprocessed: ...
    def             is_preprocessed(self)                 -> bool        : ...
    async def async_is_preprocessed(self)                 -> bool        : ...
    file             : path
    modified_time    : time
    preprocessed_file: path
    compile_flags    : list[str]
    define_macros    : dict[str, str]
    context_package  : Package



@member(Code)
@relocatable
@syncable
@unique
async def __ainit__(self: Code, file: path) -> None:
    self.file              = file
    self.modified_time     = modified_time_file(self.file)
    self.context_package   = context.package
    self.preprocessed_file = f'{self.context_package.build_code_dir}/{relative_path(from_path=self.context_package.dir, to_path=self.file)}'
    self.compile_flags     = self.context_package.compile_flags
    self.define_macros     = self.context_package.define_macros

@member(Code)
@syncable
@once
async def async_preprocess(self: Code) -> Preprocessed:
    if not await self.async_is_preprocessed():
        async with scheduler.schedule():
            await compiler.async_preprocess(
                code_file        =self.file,
                preprocessed_file=self.preprocessed_file,
                compile_flags    =self.compile_flags,
                define_macros    =self.define_macros,
                include_dirs     =[self.context_package.search_header_dir] + recursive_collect(self.context_package, next=lambda package: package.require_packages, collect=lambda package: package.install_include_dir)
            )
        self.context_package.unit_status_logger.set_code_preprocessed(code=self, preprocessed=True)
    return Preprocessed(self.preprocessed_file)

@member(Code)
@syncable
@once
async def async_is_preprocessed(self: Code) -> bool:
    return self.context_package.unit_status_logger.get_code_preprocessed(code=self)
               