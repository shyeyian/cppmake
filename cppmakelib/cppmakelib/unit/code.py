from cppmakelib.basic.config       import config
from cppmakelib.compiler.all       import compiler
from cppmakelib.executor.scheduler import scheduler
from cppmakelib.logger.unit_status import unit_status_logger
from cppmakelib.unit.package       import Package
from cppmakelib.unit.preprocessed  import Preprocessed
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, syncable, unique
from cppmakelib.utility.filesystem import path
import typing

class Code:
    def           __init__         (self, file: path) -> None        : ...
    async def    __ainit__         (self, file: path) -> None        : ...
    def             preprocess     (self)             -> Preprocessed: ...
    async def async_preprocess     (self)             -> Preprocessed: ...
    def             is_preprocessed(self)             -> bool        : ...
    async def async_is_preprocessed(self)             -> bool        : ...
    def             install        (self)             -> None        : ...
    async def async_install        (self)             -> None        : ...
    file             : path
    preprocessed_file: path
    belong_package   : Package
    compile_flags    : list[str]
    define_macros    : dict[str, str]

    if typing.TYPE_CHECKING:
        @staticmethod
        def           __new__(cls: type, file: path) -> Code: ...
        @staticmethod
        async def    __anew__(cls: type, file: path) -> Code: ...




@member(Code)
@syncable
@unique
async def __ainit__(self: Code, file: path) -> None:
    self.file              = file
    self.preprocessed_file = path()/'binary'/config.type/'code'/self.file.relative_path(from_path=path())
    self.belong_package    = Package._which_contains(self.file)
    self.compile_flags     = self.belong_package.compile_flags
    self.define_macros     = self.belong_package.define_macros

@member(Code)
@syncable
@once
async def async_preprocess(self: Code) -> Preprocessed:
    if not await self.async_is_preprocessed():
        await self.belong_package.async_build()
        async with scheduler.schedule():
            await compiler.async_preprocess(
                code_file        =self.file,
                preprocessed_file=self.preprocessed_file,
                compile_flags    =self.compile_flags,
                define_macros    =self.define_macros,
                include_dirs     =recursive_collect(self.belong_package, next=lambda package: package.depend_packages, collect=lambda package: package.include_dir)
            )
        unit_status_logger.set_code_preprocessed(code=self, result=True)
    return Preprocessed(self.preprocessed_file)

@member(Code)
@syncable
@once
async def async_is_preprocessed(self: Code) -> bool:
    return await self.belong_package.async_is_built() and \
           unit_status_logger.get_code_preprocessed(code=self)
               