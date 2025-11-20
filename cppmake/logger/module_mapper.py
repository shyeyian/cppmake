from cppmake.basic.config      import config
from cppmake.file.file_system  import create_dir
from cppmake.utility.decorator import member
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
    create_dir(f"binary/{config.type}/cache")
    self._writer = open(f"binary/{config.type}/cache/module_mapper.txt", 'w')

@member(ModuleMapperLogger)
def log_mapper(self, name, file):
    self._writer.write(f"{name} {file}\n")
    self._writer.flush()

@member(ModuleMapperLogger)
def get_mapper(self, *args, **kwargs):
    return f"binary/{config.type}/cache/module_mapper.txt"



module_mapper_logger = ModuleMapperLogger()