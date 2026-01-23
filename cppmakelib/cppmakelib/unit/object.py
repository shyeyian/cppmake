from cppmakelib.compiler.all       import compiler
from cppmakelib.logger.unit_status import unit_status_logger
from cppmakelib.system.all         import system
from cppmakelib.unit.binary        import Binary
from cppmakelib.unit.dynamic       import Dynamic
from cppmakelib.unit.executable    import Executable
from cppmakelib.unit.static        import Static
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, syncable, unique
from cppmakelib.utility.filesystem import path

class Object(Binary):
    def           __new__  (cls,  file: path) -> Object    : ...
    def           __init__ (self, file: path) -> None      : ...
    def             archive(self)             -> Static    : ...
    async def async_archive(self)             -> Static    : ...
    def             share  (self)             -> Dynamic   : ...
    async def async_share  (self)             -> Dynamic   : ...
    def             link   (self)             -> Executable: ...
    async def async_link   (self)             -> Executable: ...
    static_file    : path
    dynamic_file   : path
    executable_file: path
    require_objects: list[Object]



@member(Binary)
@unique
def __init__(self: Object, file: path) -> None:
    super(Object, self).__init__(file)
    self.static_file     = self.file.remove_extension().add_extension(system.static_suffix)
    self.dynamic_file    = self.file.remove_extension().add_extension(system.dynamic_suffix)
    self.executable_file = self.file.remove_extension().add_extension(system.executable_suffix)
    self.require_objects = [Object(file) for file in unit_status_logger.get_object_requires(object=self)]

@member(Binary)
@syncable
@once
async def async_share(self: Object) -> Dynamic:
    await compiler.async_share(
        object_file =self.file,
        dynamic_file=self.dynamic_file,
        link_flags  =self.link_flags,
        link_files  =recursive_collect(self, next=lambda object: object.require_objects, collect=lambda object: object.file, root=False)
    )
    return Dynamic(self.dynamic_file)

@member(Binary)
@syncable
@once
async def async_link(self: Object) -> Executable:
    await compiler.async_link(
        object_file    =self.file,
        executable_file=self.executable_file,
        link_flags     =self.link_flags,
        link_files     =recursive_collect(self, next=lambda object: object.require_objects, collect=lambda object: object.file, root=False)
    )
    return Executable(self.executable_file)