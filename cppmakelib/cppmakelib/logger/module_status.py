from cppmakelib.basic.config      import config
from cppmakelib.basic.exit        import on_exit
from cppmakelib.compiler.all      import compiler
from cppmakelib.file.file_system  import exist_file, create_dir, modified_time_of_file
from cppmakelib.utility.decorator import member
import json
import time

class ModuleStatusLogger:
    def __init__  (self):         ...
    def __exit__  (self):         ...
    def log_status(self, module): ...
    def get_status(self, module): ...

module_status_logger = ...



@member(ModuleStatusLogger)
def __init__(self):
    try:
        self._content = json.load(open(f'binary/cache/log.module_status.json', 'r'))
    except:
        self._content = {}
    on_exit(self.__exit__)
    
@member(ModuleStatusLogger)
def __exit__(self):
    if len(self._content) > 0:
        create_dir(f'binary/cache')
        json.dump(self._content, open(f'binary/cache/log.module_status.json', 'w'), indent=4)

@member(ModuleStatusLogger)
def log_status(self, module):
    self._content[module.name] = {
        'compiler.name'         : compiler.name,
        'compiler.path'         : compiler.path,
        'compiler.version'      : compiler.version.__str__(),
        'compiler.compile_flags': compiler.compile_flags,
        'compiler.define_macros': compiler.define_macros,
        'module.compile_flags'  : module.compile_flags,
        'module.define_macros'  : module.define_macros,
        'time'                  : time.time(),
    }

@member(ModuleStatusLogger)
def get_status(self, module):
    return module.name in self._content.keys()                                                                                                             and \
           compiler.name                             == self._content[module.name]['compiler.name'         ]                                               and \
           compiler.path                             == self._content[module.name]['compiler.path'         ]                                               and \
           compiler.version.__str__()                == self._content[module.name]['compiler.version'      ]                                               and \
           compiler.compile_flags                    == self._content[module.name]['compiler.compile_flags']                                               and \
           compiler.define_macros                    == self._content[module.name]['compiler.define_macros']                                               and \
           module.compile_flags                      == self._content[module.name]['module.compile_flags'  ]                                               and \
           module.define_macros                      == self._content[module.name]['module.define_macros'  ]                                               and \
           modified_time_of_file(module.file       ) <= self._content[module.name]['time'                  ]                                               and \
          (modified_time_of_file(module.module_file) <= self._content[module.name]['time'                  ] if exist_file(module.module_file) else False) and \
          (modified_time_of_file(module.object_file) <= self._content[module.name]['time'                  ] if exist_file(module.object_file) else False)

module_status_logger = ModuleStatusLogger()
