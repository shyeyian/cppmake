from cppmakelib.compiler.all       import compiler
from cppmakelib.unit.binary        import Binary
from cppmakelib.unit.dynamic       import Dynamic
from cppmakelib.unit.executable    import Executable
from cppmakelib.utility.algorithm  import recursive_collect
from cppmakelib.utility.decorator  import member, once, syncable, unique
from cppmakelib.utility.filesystem import iterate_dir, path

class Object(Binary):
    def           __new__    (cls,  file: path) -> Object    : ...
    def           __init__   (self, file: path) -> None      : ...
    def             share    (self)             -> Dynamic   : ...
    async def async_share    (self)             -> Dynamic   : ...
    def             is_shared(self)             -> bool      : ...
    async def async_is_shared(self)             -> bool      : ...
    def             link     (self)             -> Executable: ...
    async def async_link     (self)             -> Executable: ...
    def             is_linked(self)             -> bool      : ...
    async def async_is_linked(self)             -> bool      : ...
    static_file    : path
    dynamic_file   : path
    executable_file: path
    lib_objects    : list[Object]



@member(Object)
@unique
def __init__(self: Object, file: path) -> None:
    super(Object, self).__init__(file)
    self.lib_objects = [Object(file) for file in self.context_package.unit_status_logger.get_object_libs(object=self)]

@member(Object)
@syncable
@once
async def async_share(self: Object) -> Dynamic:
    await compiler.async_share(
        object_file =self.file,
        dynamic_file=self.dynamic_file,
        link_flags  =self.link_flags,
        lib_files   =recursive_collect(self,                 next=lambda object : object.lib_objects,       collect=lambda object : object.file) +
                     recursive_collect(self.context_package, next=lambda package: package.require_packages, collect=lambda package: [file for file in iterate_dir(package.install_lib_dir)], flatten=True)
    )
    return Dynamic(self.dynamic_file)

@member(Object)
@syncable
@once
async def async_is_shared(self: Object) -> bool:
    return self.context_package.unit_status_logger.get_object_shared(object=self)

@member(Object)
@syncable
@once
async def async_link(self: Object) -> Executable:
    await compiler.async_link(
        object_file    =self.file,
        executable_file=self.executable_file,
        link_flags     =self.link_flags,
        lib_files      =recursive_collect(self,                 next=lambda object : object.lib_objects,       collect=lambda object : object.file) +
                        recursive_collect(self.context_package, next=lambda package: package.require_packages, collect=lambda package: [file for file in iterate_dir(package.install_lib_dir)], flatten=True)
    )
    return Executable(self.executable_file)

# 1. Module.compile() -> Precompiled, Object, 需要Module(...).precompile()[0].install(), [0]来的莫名其妙, 返回struct更是莫名其妙
# 2. Module.compile() -> Precompiled, Precompiled.xxx() -> Object, 想不出xxx名字
# 3. Module.compile() -> Precompiled, 而Object直接link Precompiled本身, 不知道gcc/msvc如何支持, 且降低性能, Module需要预链接为.o的
# 4. Module.compile() -> Precompield (+ implicit Object), 可以Module(...).precompile().install, 这里Object的属性如何？

# 1. Object构造时传入所有依赖, 外部接口丑
# 2. Object由unit_status_logger记录来源于哪里，module/source->object反向记录, 需要提前Module.__anew__, 内部逻辑丑