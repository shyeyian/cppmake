from cppmakelib.basic.config      import config
from cppmakelib.file.file_system  import create_dir
from cppmakelib.utility.decorator import member
import json
import re
import time

class ModuleMapperLogger:
    def __init__  (self):                  ...
    def log_mapper(self, name, file):      ...
    def get_mapper(self, *args, **kwargs): ...

module_mapper_logger = ...

@member(ModuleMapperLogger)
def __init__(self):
    self._writer = None

@member(ModuleMapperLogger)
def log_mapper(self, name, module_file):
    if self._writer is None:
        create_dir(f"binary/cache")
        self._writer = open(f"binary/cache/log.module_mapper.txt", 'w')
    self._writer.write(f"{name} {module_file}\n")
    self._writer.flush()

@member(ModuleMapperLogger)
def get_mapper(self, *args, **kwargs):
    return f"binary/cache/log.module_mapper.txt"



module_mapper_logger = ModuleMapperLogger()