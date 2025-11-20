from cppmake.basic.config         import config
from cppmake.basic.exit           import on_exit
from cppmake.compiler.all         import compiler
from cppmake.error.logic          import LogicError
from cppmake.file.file_system     import create_dir, modified_time_of_file
from cppmake.logger.module_mapper import module_mapper_logger
from cppmake.utility.decorator    import member, syncable
from cppmake.utility.inline       import raise_
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
        self._content = {}
    self._touched = set()
    on_exit(self.__exit__)

@member(ModuleImportsLogger)
def __exit__(self):
    json.dump(self._content, open(f"binary/{config.type}/cache/module_imports.json", 'w'), indent=4)

@member(ModuleImportsLogger)
@syncable
async def async_get_imports(self, type, file):
    await self._async_touch_file(type, file)
    return self._content[file]["imports"]

@member(ModuleImportsLogger)
@syncable
async def async_get_export(self, type, file):
    await self._async_touch_file(type, file)
    return self._content[file]["export"]

@member(ModuleImportsLogger)
async def _async_touch_file(self, type, file):
    if (file not in self._content.keys() or modified_time_of_file(file) > self._content[file]["time"]):
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
            elif not file.endswith(f"{exports[0].replace('.', '/').replace(':', '/')}.cpp"):
                raise LogicError(f"module has inconsistent declaration (with file = {file}, export = {exports[0]})")
            export = exports[0]
            imports = [import_ if not import_.startswith(':') else f"{export.split(':')[0]}{import_}" for import_ in imports]
        else:
            export = None
            imports = re.findall(r'^\s*(?:export\s+)?import\s+([\w\.:]+)\s*;\s*$', code, flags=re.MULTILINE)
        self._content[file] = {
            "time"   : time.time(),
            "export" : export,
            "imports": imports
        }

module_imports_logger = ModuleImportsLogger()