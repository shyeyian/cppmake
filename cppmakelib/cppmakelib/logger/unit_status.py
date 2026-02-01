from cppmakelib.compiler.all       import compiler
from cppmakelib.error.logic        import LogicError
from cppmakelib.unit.code          import Code
from cppmakelib.unit.module        import Module
from cppmakelib.unit.source        import Source
from cppmakelib.utility.filesystem import path
from cppmakelib.utility.decorator  import member
import json
import re
import typing

class UnitStatusLogger:
    # ========
    def __init__                          (self, build_cache_dir: path)                     -> None      : ...
    def __del__                           (self)                                            -> None      : ...
    # ========
    def             get_code_preprocessed (self, code  : Code)                              -> bool      : ...
    def             set_code_preprocessed (self, code  : Code,    preprocessed: bool)       -> None      : ...
    # ========
    async def async_get_module_name       (self, module: Module)                            -> str       : ...
    def             set_module_name       (self, module: Module,  name        : str)        -> None      : ...
    async def async_get_module_imports    (self, module: Module)                            -> list[path]: ...
    def             set_module_imports    (self, module: Module,  imports     : list[path]) -> None      : ...
    def             get_module_precompiled(self, module: Module)                            -> bool      : ...
    def             set_module_precompiled(self, module: Module,  precompiled : bool)       -> None      : ...
    # ========
    async def async_get_source_imports    (self, source: Source)                            -> list[path]: ...
    def             set_source_imports    (self, source: Source,  imports     : list[path]) -> None      : ...
    def             get_source_compiled   (self, source: Source)                            -> bool      : ...
    def             set_source_compiled   (self, source: Source,  compiled    : bool)       -> None      : ...
    # ========

    def _get(self, entry: list[str], check: dict[str, typing.Any], result: str)                   -> typing.Any | typing.Literal[False]: ...
    def _set(self, entry: list[str], check: dict[str, typing.Any], result: dict[str, typing.Any]) -> None                              : ...
    def _reflect(self, object: object) -> dict[str, typing.Any]: ...
    _content : typing.Any
    _noreflect: list[str] = [
        'context_package', 'preprocessed_file', 'preparsed_file', 'precompiled_file', 'object_file'
    ]


@member(UnitStatusLogger)
def __init__(self: UnitStatusLogger, build_cache_dir: path) -> None:
    try:
        self._content = json.load(open(f'{build_cache_dir}/unit_status.json', 'r'))
    except:
        self._content = {
            'code': {
                'preprocessed': {}
            },
            'header': {
                'includes': {},
                'preparsed': {}
            },
            'module': {
                'name': {},
                'file': {},
                'includes': {},
                'imports': {},
                'precompiled': {}
            },
            'source': {
                'includes': {},
                'imports': {},
                'compiled': {}
            },
            'object': {
                'requires': {}
            }
        }

@member(UnitStatusLogger)
def get_code_preprocessed(self: UnitStatusLogger, code: Code) -> bool:
    return self._get(entry=['code', 'preprocessed', code.file], check={'code': code, 'compiler': compiler}, result='preprocessed')

@member(UnitStatusLogger)
def set_code_preprocessed(self: UnitStatusLogger, code: Code, preprocessed: bool) -> None:
    return self._set(entry=['code', 'preprocessed', code.file], check={'code': code, 'compiler': compiler}, result={'preprocessed': preprocessed})

@member(UnitStatusLogger)
async def async_get_module_name(self: UnitStatusLogger, module: Module) -> str:
    name = self._get(entry=['module', 'name', module.file], check={'module': module, 'compiler': compiler}, result='name')
    if name is False:
        await module.async_preprocess()
        statements = re.findall(
            pattern=r'^\s*(export\s+)?module\s+(\w+([\.:]\w+)*)\s*;\s*$',
            string =open(module.preprocessed_file).read(),
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
    return self._set(entry=['module', 'name', module.file], check={'module': module, 'compiler': compiler}, result={'name': name})

@member(UnitStatusLogger)
async def async_get_module_imports(self: UnitStatusLogger, module: Module) -> list[path]:
    imports = self._get(entry=['module', 'imports', module.file], check={'module':  module, 'compiler': compiler}, result='imports')
    if imports is False:
        await module.async_preprocess()
        statements = re.findall(
            pattern=r'^\s*import\s+module\s+(\w+([\.:]\w+)*)\s*;\s$',
            string =open(module.preprocessed_file, 'r').read(),
            flags  =re.MULTILINE
        )
        imports = [f'{module.context_package.search_module_dir}/{statement.group(1).replace('.', '/').replace(':', '/')}' for statement in statements]
        self.set_module_imports(module=module, imports=imports)
    return imports

@member(UnitStatusLogger)
def set_module_imports(self: UnitStatusLogger, module: Module, imports: list[path]) -> None:
    return self._set(entry=['module', 'imports', module.file], check={'module': module, 'compiler': compiler}, result={'imports': imports})

@member(UnitStatusLogger)
def get_module_precompiled(self: UnitStatusLogger, module: Module) -> bool:
    return self._get(entry=['module', 'precompiled', module.file], check={'module': module, 'compiler': compiler}, result='precompiled')
    
@member(UnitStatusLogger)
def set_module_precompiled(self: UnitStatusLogger, module: Module, precompiled: bool) -> None:
    return self._set(entry=['module', 'precompiled', module.file], check={'module': module, 'compiler': compiler}, result={'precompiled': precompiled})

@member(UnitStatusLogger)
async def async_get_source_imports(self: UnitStatusLogger, source: Source) -> list[path]:
    imports = self._get(entry=['source', 'imports', source.file], check={'source': source, 'compiler': compiler}, result='imports')
    if imports is False:
        await source.async_preprocess()
        statements = re.findall(
            pattern=r'^\s*import\s+module\s+(\w+([\.:]\w+)*)\s*;\s$',
            string =open(source.preprocessed_file, 'r').read(),
            flags  =re.MULTILINE
        )
        imports = [f'{source.context_package.search_module_dir}/{statement.group(1).replace('.', '/').replace(':', '/')}' for statement in statements]
        self.set_source_imports(source=source, imports=imports)
    return imports

@member(UnitStatusLogger)
def set_source_imports(self: UnitStatusLogger, source: Source, imports: list[path]) -> None:
    return self._set(entry=['source', 'imports', source.file], check={'source': source, 'compiler': compiler}, result={'imports': imports})

@member(UnitStatusLogger)
def get_source_compiled(self: UnitStatusLogger, source: Source) -> bool:
    return self._get(entry=['source', 'compiled', source.file], check={'source': source, 'compiler': compiler}, result='compiled')

@member(UnitStatusLogger)
def set_source_compiled(self: UnitStatusLogger, source: Source, compiled: bool) -> None:
    return self._set(entry=['source', 'compiled', source.file], check={'source': source, 'compiler': compiler}, result={'compiled': compiled})        

@member(UnitStatusLogger)
def _get(self: UnitStatusLogger, entry: list[str], check: dict[str, typing.Any], result: str) -> typing.Any | typing.Literal[False]:
    ptr = self._content
    for subentry in entry:
        try:
            ptr = ptr[subentry]
        except KeyError:
            return False
    for subcheck in check.keys():
        if ptr[subcheck] != self._reflect(ptr[subcheck]):
            return False
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
        