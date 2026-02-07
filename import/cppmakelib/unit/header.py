from cppmakelib.unit.code import Code

class Header(Code):
    def           __new__       (cls: ..., file: path) -> Header   : ...
    async def    __anew__       (cls: ..., file: path) -> Header   : ...
    def           __init__      (self,     file: path) -> None     : ...
    async def    __ainit__      (self,     file: path) -> None     : ...
    def             preparse    (self)                 -> Preparsed: ...
    async def async_preparse    (self)                 -> Preparsed: ...
    def             is_preparsed(self)                 -> bool     : ...
    async def async_is_preparsed(self)                 -> bool     : ...
    name            : str
    preparsed_file  : path
    object_file     : path
    diagnostic_file : path
    include_headers : list[Header]



from cppmakelib.compiler.all       import compiler
from cppmakelib.executor.operation import when_all
from cppmakelib.executor.scheduler import scheduler
from cppmakelib.unit.preparsed     import Preparsed
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, relocatable, syncable, unique
from cppmakelib.utility.filesystem import path, relative_path

@member(Header)
@syncable
@unique
@relocatable
async def __ainit__(self: Header, file: path) -> None:
    await super(Header, self).__ainit__(file)
    self.name            = relative_path(from_path=self.context_package.search_header_dir, to_path=self.file)
    self.preparsed_file  = f'{self.context_package.build_header_dir}/{self.name}{compiler.preparsed_suffix}'
    self.diagnostic_file = f'{self.context_package.build_header_dir}/{self.name}{compiler.diagnostic_suffix}'
    self.include_headers = await when_all([Header.__anew__(Header, file) for file in self.context_package.unit_status_logger.get_header_includes(header=self)])

@member(Header)
@syncable
@once
async def async_preparse(self: Header) -> Preparsed:
    if not await self.async_is_preparsed():
        await when_all([header.async_preparse() for header in self.include_headers])
        await self.async_preprocess()
        async with scheduler.schedule():
            await compiler.async_preparse(
                header_file    =self.file,
                preparsed_file =self.preparsed_file,
                compile_flags  =self.compile_flags,
                define_macros  =self.define_macros,
                include_dirs   =[self.context_package.build_header_dir] + recursive_collect(self.context_package, next=lambda package: package.require_packages, collect=lambda package: package.install_include_dir),
                diagnostic_file=self.diagnostic_file
            )
        self.context_package.unit_status_logger.set_header_preparsed(header=self, result=True)
    return Preparsed(self.preparsed_file)

@member(Header)
@syncable
@once
async def async_is_preparsed(self: Header) -> bool:
    return all(await when_all([header.async_is_preparsed() for header in self.include_headers])) and \
           await self.async_is_preparsed()                                                       and \
           self.context_package.unit_status_logger.get_header_preparsed(header=self)