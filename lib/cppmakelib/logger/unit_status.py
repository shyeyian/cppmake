from cppmakelib.compiler.all       import compiler
from cppmakelib.error.logic        import LogicError
from cppmakelib.executor.operation import when_all
from cppmakelib.unit.code          import Code
from cppmakelib.unit.module        import Module
from cppmakelib.unit.object        import Object
from cppmakelib.unit.source        import Source
from cppmakelib.utility.decorator  import member
from cppmakelib.utility.filesystem import create_dir, parent_dir, path
import json
import re
import typing

class UnitStatusLogger:
    # ========
    def           __init__                (self, build_utility_dir: path)                   -> None      : ...
    def           __del__                 (self)                                            -> None      : ...
    # ========
    def             get_code_preprocessed (self, code  : Code)                              -> bool      : ...
    def             set_code_preprocessed (self, code  : Code,    preprocessed: bool)       -> None      : ...
    # ========
    async def async_get_module_name       (self, module: Module)                            -> str       : ...
    def             set_module_name       (self, module: Module,  name        : str)        -> None      : ...
    async def async_get_module_imports    (self, module: Module)                            -> list[path]: ...
    async def async_set_module_imports    (self, module: Module,  imports     : list[path]) -> None      : ...
    def             get_module_precompiled(self, module: Module)                            -> bool      : ...
    def             set_module_precompiled(self, module: Module,  precompiled : bool)       -> None      : ...
    # ========
    async def async_get_source_imports    (self, source: Source)                            -> list[path]: ...
    async def async_set_source_imports    (self, source: Source,  imports     : list[path]) -> None      : ...
    def             get_source_compiled   (self, source: Source)                            -> bool      : ...
    def             set_source_compiled   (self, source: Source,  compiled    : bool)       -> None      : ...
    # ========
    def             get_object_libs       (self, object: Object)                            -> list[path]: ...
    def             set_object_libs       (self, object: Object,  libs        : list[path]) -> None      : ...
    def             get_object_shared     (self, object: Object)                            -> bool      : ...
    def             set_object_shared     (self, object: Object,  shared      : bool)       -> None      : ...
    def             get_object_linked     (self, object: Object)                            -> bool      : ...
    def             set_object_linked     (self, object: Object,  linked      : bool)       -> None      : ...
    # ========

    class _StatusNotFoundError(KeyError):
        pass
    def _get    (self, entry: list[str], check: dict[str, typing.Any], result: str)                   -> typing.Any           : ...
    def _set    (self, entry: list[str], check: dict[str, typing.Any], result: dict[str, typing.Any]) -> None                 : ...
    def _reflect(self, object: object)                                                                -> dict[str, typing.Any]: ...
    _file   : path
    _content: typing.Any
    


@member(UnitStatusLogger)
def __init__(self: UnitStatusLogger, build_utility_dir: path) -> None:
    self._file = f'{build_utility_dir}/unit_status.json'
    try:
        self._content = json.load(open(self._file, 'r'))
    except:
        self._content = {}

@member(UnitStatusLogger)
def __del__(self: UnitStatusLogger) -> None:
    create_dir(parent_dir(self._file))
    json.dump(self._content, open(self._file, 'w'), indent=4)

@member(UnitStatusLogger)
def get_code_preprocessed(self: UnitStatusLogger, code: Code) -> bool:
    try:
        return self._get(entry=['code', 'preprocessed', code.file], check={'code': code, 'compiler': compiler}, result='preprocessed')
    except UnitStatusLogger._StatusNotFoundError:
        return False

@member(UnitStatusLogger)
def set_code_preprocessed(self: UnitStatusLogger, code: Code, preprocessed: bool) -> None:
    self._set(entry=['code', 'preprocessed', code.file], check={'code': code, 'compiler': compiler}, result={'preprocessed': preprocessed})

@member(UnitStatusLogger)
async def async_get_module_name(self: UnitStatusLogger, module: Module) -> str:
    try:
        name = self._get(entry=['module', 'name', module.file], check={'module': module, 'compiler': compiler}, result='name')
    except UnitStatusLogger._StatusNotFoundError:
        await module.async_preprocess()
        statements = re.findall(
            pattern=r'^\s*(export\s+)?module\s+(\w+([\.:]\w+)*)\s*;\s*$',
            string =open(module.preprocessed_file, 'r').read(),
            flags  =re.MULTILINE
        )
        if len(statements) == 0:
            raise LogicError(f'module {module.file} does not have a export statement')
        elif len(statements) == 1:
            name = statements[0].group(2)
            self.set_module_name(module=module, name=name)
        else: # len(exports) >= 2:
            raise LogicError(f'module {module.file} has multiple export statements (with statements = {statements})')
    return name
        
@member(UnitStatusLogger)
def set_module_name(self: UnitStatusLogger, module: Module, name: str) -> None:
    self._set(entry=['module', 'name', module.file], check={'module': module, 'compiler': compiler}, result={'name': name})

@member(UnitStatusLogger)
async def async_get_module_imports(self: UnitStatusLogger, module: Module) -> list[path]:
    try:
        imports = self._get(entry=['module', 'imports', module.file], check={'module':  module, 'compiler': compiler}, result='imports')
    except UnitStatusLogger._StatusNotFoundError:
        await module.async_preprocess()
        statements = re.findall(
            pattern=r'^\s*(export\s+)?import\s+module\s+(\w+([\.:]\w+)*)\s*;\s$',
            string =open(module.preprocessed_file, 'r').read(),
            flags  =re.MULTILINE
        )
        imports = [f'{module.context_package.import_dir}/{statement.group(2).replace('.', '/').replace(':', '/')}.cpp' for statement in statements]
        await self.async_set_module_imports(module=module, imports=imports)
    return imports

@member(UnitStatusLogger)
async def async_set_module_imports(self: UnitStatusLogger, module: Module, imports: list[path]) -> None:
    self._set(entry=['module', 'imports', module.file],        check={'module': module,                     'compiler': compiler}, result={'imports': imports})
    self._set(entry=['object', 'libs',    module.object_file], check={'object': Object(module.object_file), 'compiler': compiler}, result={'libs'   : [module.object_file for module in await when_all([Module.__anew__(Module, import_) for import_ in imports])]})

@member(UnitStatusLogger)
def get_module_precompiled(self: UnitStatusLogger, module: Module) -> bool:
    try:
        return self._get(entry=['module', 'precompiled', module.file], check={'module': module, 'compiler': compiler}, result='precompiled')
    except UnitStatusLogger._StatusNotFoundError:
        return False

@member(UnitStatusLogger)
def set_module_precompiled(self: UnitStatusLogger, module: Module, precompiled: bool) -> None:
    self._set(entry=['module', 'precompiled', module.file], check={'module': module, 'compiler': compiler}, result={'precompiled': precompiled})

@member(UnitStatusLogger)
async def async_get_source_imports(self: UnitStatusLogger, source: Source) -> list[path]:
    try:
        imports = self._get(entry=['source', 'imports', source.file], check={'source': source, 'compiler': compiler}, result='imports')
    except UnitStatusLogger._StatusNotFoundError:
        await source.async_preprocess()
        statements = re.findall(
            pattern=r'^\s*import\s+module\s+(\w+([\.:]\w+)*)\s*;\s$',
            string =open(source.preprocessed_file, 'r').read(),
            flags  =re.MULTILINE
        )
        imports = [f'{source.context_package.import_dir}/{statement.group(1).replace('.', '/').replace(':', '/')}.cpp' for statement in statements]
        await self.async_set_source_imports(source=source, imports=imports)
    return imports

@member(UnitStatusLogger)
async def async_set_source_imports(self: UnitStatusLogger, source: Source, imports: list[path]) -> None:
    self._set(entry=['source', 'imports', source.file],        check={'source': source,                     'compiler': compiler}, result={'imports': imports})
    self._set(entry=['object', 'libs',    source.object_file], check={'object': Object(source.object_file), 'compiler': compiler}, result={'libs'   : [module.object_file for module in await when_all([Module.__anew__(Module, import_) for import_ in imports])]})

@member(UnitStatusLogger)
def get_source_compiled(self: UnitStatusLogger, source: Source) -> bool:
    try:
        return self._get(entry=['source', 'compiled', source.file], check={'source': source, 'compiler': compiler}, result='compiled')
    except UnitStatusLogger._StatusNotFoundError:
        return False

@member(UnitStatusLogger)
def set_source_compiled(self: UnitStatusLogger, source: Source, compiled: bool) -> None:
    self._set(entry=['source', 'compiled', source.file], check={'source': source, 'compiler': compiler}, result={'compiled': compiled})        

@member(UnitStatusLogger)
def get_object_libs(self: UnitStatusLogger, object: Object) -> list[path]:
    try:
        return self._get(entry=['object', 'libs', object.file], check={'object': object, 'compiler': compiler}, result='libs')
    except UnitStatusLogger._StatusNotFoundError:
        raise LogicError(f'object does not have a libs cache (from a module or source)')

@member(UnitStatusLogger)
def set_object_libs(self: UnitStatusLogger, object: Object, libs: list[path]) -> None:
    self._set(entry=['object', 'libs', object.file], check={'object': object, 'compiler': compiler}, result={'libs': libs})

@member(UnitStatusLogger)
def get_object_shared(self: UnitStatusLogger, object: Object) -> bool:
    try:
        return self._get(entry=['object', 'shared', object.file], check={'object': object, 'compiler': compiler}, result='shared')
    except UnitStatusLogger._StatusNotFoundError:
        return False
    
@member(UnitStatusLogger)
def set_object_shared(self: UnitStatusLogger, object: Object, shared: bool) -> None:
    self._set(entry=['object', 'shared', object.file], check={'object': object, 'compiler': compiler}, result={'shared': shared})

@member(UnitStatusLogger)
def get_object_linked(self: UnitStatusLogger, object: Object) -> bool:
    try:
        return self._get(entry=['object', 'linked', object.file], check={'object': object, 'compiler': compiler}, result='linked')
    except UnitStatusLogger._StatusNotFoundError:
        return False
    
@member(UnitStatusLogger)
def set_object_linked(self: UnitStatusLogger, object: Object, linked: bool) -> None:
    self._set(entry=['object', 'linked', object.file], check={'object': object, 'compiler': compiler}, result={'linked': linked})

@member(UnitStatusLogger)
def _get(self: UnitStatusLogger, entry: list[str], check: dict[str, typing.Any], result: str) -> typing.Any:
    ptr = self._content
    for subentry in entry:
        if subentry not in ptr.keys():
            raise UnitStatusLogger._StatusNotFoundError()
        ptr = ptr[subentry]
    for subcheck in check.keys():
        if ptr[subcheck] != self._reflect(ptr[subcheck]):
            raise UnitStatusLogger._StatusNotFoundError()
    return ptr[result]

@member(UnitStatusLogger)
def _set(self: UnitStatusLogger, entry: list[str], check: dict[str, typing.Any], result: dict[str, typing.Any]) -> None:
    ptr = self._content
    for subentry in entry:
        if subentry not in ptr.keys():
            ptr[subentry] = {}
        ptr = ptr[subentry]
    for subcheck in check.keys():
        ptr[subcheck] = self._reflect(check[subcheck])
    for subresult in result.keys():
        ptr[subresult] = self._reflect(result[subresult])

@member(UnitStatusLogger)
def _reflect(self: UnitStatusLogger, object: object) -> dict[str, typing.Any]:
    reflected = vars(object)
    for key, value in reflected.items():
        if hasattr(value, '__dict__'):
            reflected[key] = '...'
        elif isinstance(value, list):
            for index, subvalue in enumerate(typing.cast(list[object], value)):
                value[index] = self._reflect(subvalue)
        else:
            reflected.pop(key)
    return reflected
        