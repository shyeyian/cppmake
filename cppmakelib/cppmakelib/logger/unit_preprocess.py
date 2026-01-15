from cppmakelib.basic.config         import config
from cppmakelib.basic.exit           import on_exit
from cppmakelib.compiler.all         import compiler
from cppmakelib.error.logic          import LogicError
from cppmakelib.execution.scheduler  import scheduler
from cppmakelib.file.file_system     import create_dir, modified_time_of_file
from cppmakelib.logger.module_mapper import module_mapper_logger
from cppmakelib.utility.decorator    import member, syncable
from cppmakelib.utility.inline       import raise_
import json
import re
import time

class UnitPreprocessLogger:
    def           __init__      (self):       ...
    def           __exit__      (self):       ...
    def             get_imports (self, unit): ...
    async def async_get_imports (self, unit): ...
    def             get_export  (self, file): ...
    async def async_get_export  (self, file): ...

unit_preprocess_logger = ...



@member(UnitPreprocessLogger)
def __init__(self):
    try:
        self._content = json.load(open(f'binary/cache/log.unit_preprocess.json', 'r'))
    except:
        self._content = {
            'file' : {},
            'unit' : {
                'module': {},
                'source': {},
            },
        }
    self._updated = set()
    on_exit(self.__exit__)

@member(UnitPreprocessLogger)
def __exit__(self):
    if len(self._content['file']) > 0:
        create_dir(f'binary/cache')
        json.dump(self._content, open(f'binary/cache/log.unit_preprocess.json', 'w'), indent=4)

@member(UnitPreprocessLogger)
@syncable
async def async_get_imports(self, unit):
    await self._async_update_content(type=type(unit).__qualname__.lower(), file=unit.file, name=unit.name)
    return self._content['file'][self._content['unit'][type(unit).__qualname__.lower()][unit.name]['unit.file']]['unit.imports']

@member(UnitPreprocessLogger)
@syncable
async def async_get_export(self, file):
    await self._async_update_content(type='module', file=file)
    return self._content['file'][file]['unit.export']

@member(UnitPreprocessLogger)
async def _async_update_content(self, type, file, name=None):
    updated = file in self._content['file'].keys()                                                 and \
              compiler.name               == self._content['file'][file]['compiler.name'         ] and \
              compiler.path               == self._content['file'][file]['compiler.path'         ] and \
              compiler.version.__str__()  == self._content['file'][file]['compiler.version'      ] and \
              compiler.compile_flags      == self._content['file'][file]['compiler.compile_flags'] and \
              compiler.define_macros      == self._content['file'][file]['compiler.define_macros'] and \
              modified_time_of_file(file) <= self._content['file'][file]['time'                  ]
    if not updated:
        code = await compiler.async_preprocess(file=file)
        if type == 'module':
            exports = re.findall(r'^\s*(?:export\s+)?module\s+([\w\.:]+)\s*;\s*$', code, flags=re.MULTILINE)
            imports = re.findall(r'^\s*(?:export\s+)?import\s+([\w\.:]+)\s*;\s*$', code, flags=re.MULTILINE)
            if len(exports) == 0:
                raise LogicError(f'module does not have an export declaration (with file = {file})')
            elif len(exports) >= 2:
                raise LogicError(f'module has ambiguous export declarations (with file = {file}, exports = {{{', '.join(exports)}}})')
            elif (name is not None and exports[0] != name) or (name is None and not file.endswith(f'{exports[0].replace('.', '/').replace(':', '/')}.cpp')):
                raise LogicError(f'module has inconsistent declaration (with file = {file}, export = {exports[0]})')
            export = exports[0]
            imports = [import_ if not import_.startswith(':') else f'{export.split(':')[0]}{import_}' for import_ in imports]
            if name is None:
                name = export
        else:
            export = None
            imports = re.findall(r'^\s*(?:export\s+)?import\s+([\w\.:]+)\s*;\s*$', code, flags=re.MULTILINE)
        self._content['file'][file] = {
            'unit.type'             : type,
            'unit.name'             : name,
            'unit.export'           : export,
            'unit.imports'          : imports,
            'compiler.name'         : compiler.name,
            'compiler.path'         : compiler.path,
            'compiler.version'      : compiler.version.__str__(),
            'compiler.compile_flags': compiler.compile_flags,
            'compiler.define_macros': compiler.define_macros,
            'time'                  : time.time(),
        }
        self._content['unit'][type][name] = {
            'unit.file': file
        }
    self._updated |= {(type, name)}
    if type == 'module' and name is not None:
        self._check_cycle(type=type, name=name)

@member(UnitPreprocessLogger)
def _check_cycle(self, type, name, history=[]):
    assert type == 'module'
    if name in history:
        raise LogicError(f'module import cycle (with cycle = {' -> '.join(history + [name])})')
    pkghist = [histname.split(':')[0].split('.')[0] for histname in history]
    pkgname = name.split(':')[0].split('.')[0]
    if pkgname in pkghist and pkgname != pkghist[-1]:
        raise LogicError(f'package import cycle (with module-cycle = {' -> '.join(history + [name])}, package-cycle = {'->'.join(pkghist + [pkgname])})')
    for subname in self._content['file'][self._content['unit']['module'][name]['unit.file']]['unit.imports']:
        if (type, subname) in self._updated:
            self._check_cycle(type=type, name=subname, history=history + [name])
        
unit_preprocess_logger = UnitPreprocessLogger()