from cppmakelib.basic.config      import config
from cppmakelib.basic.exit        import on_exit
from cppmakelib.builder.git       import git
from cppmakelib.compiler.all      import compiler
from cppmakelib.file.file_system  import exist_dir, create_dir, modified_time_of_file, modified_time_of_dir
from cppmakelib.utility.decorator import member, syncable
import json
import time

class PackageStatusLogger:
    def           __init__    (self):          ...
    def           __exit__    (self):          ...
    def             log_status(self, package): ...
    async def async_log_status(self, package): ...
    def             get_status(self, package): ...
    async def async_get_status(self, package): ...

package_status_logger = ...



@member(PackageStatusLogger)
def __init__(self):
    try:
        self._content = json.load(open(f'binary/cache/log.package_status.json', 'r'))
    except:
        self._content = {}
    on_exit(self.__exit__)
    
@member(PackageStatusLogger)
def __exit__(self):
    if len(self._content) > 0:
        create_dir(f'binary/cache')
        json.dump(self._content, open(f'binary/cache/log.package_status.json', 'w'), indent=4)

@member(PackageStatusLogger)
@syncable
async def async_log_status(self, package):
    self._content[package.name] = {
        'compiler.name'           : compiler.name,
        'compiler.path'           : compiler.path,
        'compiler.version'        : compiler.version.__str__(),
        'compiler.compile_flags'  : compiler.compile_flags,
        'compiler.link_flags'     : compiler.link_flags,
        'compiler.define_macros'  : compiler.define_macros,
        'package.compile_flags'   : package.compile_flags,
        'package.link_flags'      : package.link_flags,
        'package.define_macros'   : package.define_macros,
        'git.log(package.git_dir)': await git.async_log(package.git_dir) if package.git_dir is not None else None,
        'time'                    : time.time()
    }

@member(PackageStatusLogger)
@syncable
async def async_get_status(self, package):
    return package.name in self._content.keys()                                                                                                                                                      and \
           compiler.name                                                                  == self._content[package.name]['compiler.name'           ]                                                 and \
           compiler.path                                                                  == self._content[package.name]['compiler.path'           ]                                                 and \
           compiler.version.__str__()                                                     == self._content[package.name]['compiler.version'        ]                                                 and \
           compiler.compile_flags                                                         == self._content[package.name]['compiler.compile_flags'  ]                                                 and \
           compiler.link_flags                                                            == self._content[package.name]['compiler.link_flags'     ]                                                 and \
           compiler.define_macros                                                         == self._content[package.name]['compiler.define_macros'  ]                                                 and \
           package.compile_flags                                                          == self._content[package.name]['package.compile_flags'   ]                                                 and \
           package.link_flags                                                             == self._content[package.name]['package.link_flags'      ]                                                 and \
           package.define_macros                                                          == self._content[package.name]['package.define_macros'   ]                                                 and \
          (await git.async_log(package.git_dir) if package.git_dir is not None else None) == self._content[package.name]['git.log(package.git_dir)']                                                 and \
          (modified_time_of_dir (package.git_dir     )                                    <= self._content[package.name]['time'                    ] if package.git_dir      is not None else True ) and \
          (modified_time_of_dir (package.module_dir  )                                    <= self._content[package.name]['time'                    ] if package.module_dir   is not None else True ) and \
          (modified_time_of_file(package.cppmake_file)                                    <= self._content[package.name]['time'                    ] if package.cppmake_file is not None else True ) and \
          (modified_time_of_dir (package.build_dir   )                                    <= self._content[package.name]['time'                    ] if exist_dir(package.build_dir  )   else False) and \
          (modified_time_of_dir (package.install_dir )                                    <= self._content[package.name]['time'                    ] if exist_dir(package.install_dir)   else False) 

package_status_logger = PackageStatusLogger()
