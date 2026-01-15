from cppmakelib.basic.config      import config
from cppmakelib.basic.exit        import on_exit
from cppmakelib.compiler.all      import compiler
from cppmakelib.file.file_system  import exist_file, create_dir, modified_time_of_file
from cppmakelib.utility.decorator import member
import json
import time

class SourceStatusLogger:
    def __init__  (self):         ...
    def __exit__  (self):         ...
    def log_status(self, source): ...
    def get_status(self, source): ...

source_status_logger = ...



@member(SourceStatusLogger)
def __init__(self):
    try:
        self._content = json.load(open(f'binary/cache/log.source_status.json', 'r'))
    except:
        self._content = {}
    on_exit(self.__exit__)
    
@member(SourceStatusLogger)
def __exit__(self):
    if len(self._content) > 0:
        create_dir(f'binary/cache')
        json.dump(self._content, open(f'binary/cache/log.source_status.json', 'w'), indent=4)

@member(SourceStatusLogger)
def log_status(self, source):
    self._content[source.name] = {
        'compiler.name'         : compiler.name,
        'compiler.path'         : compiler.path,
        'compiler.version'      : compiler.version.__str__(),
        'compiler.compile_flags': compiler.compile_flags,
        'compiler.link_flags'   : compiler.link_flags,
        'compiler.define_macros': compiler.define_macros,
        'source.compile_flags'  : source.compile_flags,
        'source.link_flags'     : source.link_flags,
        'source.define_macros'  : source.define_macros,
        'time'                  : time.time(),
    }

@member(SourceStatusLogger)
def get_status(self, source):
    return source.name in self._content.keys()                                                                                                                     and \
           compiler.name                                 == self._content[source.name]['compiler.name'         ]                                                   and \
           compiler.path                                 == self._content[source.name]['compiler.path'         ]                                                   and \
           compiler.version.__str__()                    == self._content[source.name]['compiler.version'      ]                                                   and \
           compiler.compile_flags                        == self._content[source.name]['compiler.compile_flags']                                                   and \
           compiler.link_flags                           == self._content[source.name]['compiler.link_flags'   ]                                                   and \
           compiler.define_macros                        == self._content[source.name]['compiler.define_macros']                                                   and \
           source.compile_flags                          == self._content[source.name]['source.compile_flags'  ]                                                   and \
           source.link_flags                             == self._content[source.name]['source.link_flags'     ]                                                   and \
           source.define_macros                          == self._content[source.name]['source.define_macros'  ]                                                   and \
           modified_time_of_file(source.file           ) <= self._content[source.name]['time'                  ]                                                   and \
          (modified_time_of_file(source.executable_file) <= self._content[source.name]['time'                  ] if exist_file(source.executable_file) else False)

source_status_logger = SourceStatusLogger()
