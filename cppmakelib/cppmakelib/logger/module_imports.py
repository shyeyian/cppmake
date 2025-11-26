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

class ModuleImportsLogger:
    def           __init__      (self):             ...
    def           __exit__      (self):             ...
    def             get_imports (self, type, file): ...
    async def async_get_imports (self, type, file): ...
    def             get_export  (self, type, file): ...
    async def async_get_export  (self, type, file): ...

module_imports_logger = ...



@member(ModuleImportsLogger)
def __init__(self):
    create_dir(f"binary/{config.type}/cache")
    try:
        self._content = json.load(open(f"binary/{config.type}/cache/module_imports.json", 'r'))
    except:
        self._content = {
            "file"  : {},
            "module": {},
            "source": {},
        }
    self._updated = set()
    on_exit(self.__exit__)

@member(ModuleImportsLogger)
def __exit__(self):
    json.dump(self._content, open(f"binary/{config.type}/cache/module_imports.json", 'w'), indent=4)

@member(ModuleImportsLogger)
@syncable
async def async_get_imports(self, type, name, file):
    await self._async_update_content(type=type, file=file, name=name)
    return self._content["file"][file]["imports"]

@member(ModuleImportsLogger)
@syncable
async def async_get_export(self, type, file):
    await self._async_update_content(type=type, file=file)
    return self._content["file"][file]["export"]

@member(ModuleImportsLogger)
async def _async_update_content(self, type, file, name=None):
    from cppmakelib.unit.module import Module
    if file not in self._content["file"].keys() or modified_time_of_file(file) > self._content["file"][file]["time"]:
        async with scheduler.schedule():
            code = open(file, 'r').read()
            code = re.sub(r'^\s*#include\s*(?!<version>).*$', "", code, flags=re.MULTILINE)
            code = await compiler.async_preprocess(code=code)
        if type == "module":
            exports = re.findall(r'^\s*export\s+module\s+([\w\.:]+)\s*;\s*$',      code, flags=re.MULTILINE)
            imports = re.findall(r'^\s*(?:export\s+)?import\s+([\w\.:]+)\s*;\s*$', code, flags=re.MULTILINE)
            if len(exports) == 0:
                raise LogicError(f"module does not have an export declaration (with file = {file})")
            elif len(exports) >= 2:
                raise LogicError(f"module has ambiguous export declarations (with file = {file}, exports = {{{', '.join(exports)}}})")
            elif (name is not None and exports[0] != name) or (name is None and not file.endswith(f"{exports[0].replace('.', '/').replace(':', '/')}.cpp")):
                raise LogicError(f"module has inconsistent declaration (with file = {file}, export = {exports[0]})")
            export = exports[0]
            imports = [import_ if not import_.startswith(':') else f"{export.split(':')[0]}{import_}" for import_ in imports]
            if name is None:
                name = export
        else:
            export = None
            imports = re.findall(r'^\s*(?:export\s+)?import\s+([\w\.:]+)\s*;\s*$', code, flags=re.MULTILINE)
        self._content["file"][file] = {
            "time"   : time.time(),
            "type"   : type,
            "export" : export,
            "imports": imports
        }
        self._content[type][name] = {
            "time"   : time.time(),
            "imports": imports
        }
    self._updated |= {(type, name)}
    if type == "module" and name is not None:
        self._check_cycle(type=type, name=name)

@member(ModuleImportsLogger)
def _check_cycle(self, type, name, history=[]):
    assert type == "module"
    if name in history:
        raise LogicError(f"module import cycle (with cycle = {'->'.join(history + [name])})")
    pkghist = [histname.split(':')[0].split('.')[0] for histname in history]
    pkgname = name.split(':')[0].split('.')[0]
    if pkgname in pkghist and pkgname != pkghist[-1]:
        raise LogicError(f"package import cycle (with module-cycle = {'->'.join(history + [name])}, package-cycle = {'->'.join(pkghist + [pkgname])})")
    for subname in self._content["module"][name]["imports"]:
        if (type, subname) in self._updated:
            self._check_cycle(type=type, name=subname, history=history + [name])
        
    

module_imports_logger = ModuleImportsLogger()