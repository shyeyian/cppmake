from cppmake.basic.exit        import on_exit
from cppmake.file.file_system  import absolute_path, create_dir
from cppmake.utility.decorator import member
import json

class CompileCommandsLogger:
    def __init__   (self):                     ...
    def __exit__   (self):                     ...
    def log_command(self, command, file): ...
    
compile_commands_logger = ...



@member(CompileCommandsLogger)
def __init__(self):
    create_dir("binary/cache")
    try:
        self._content = json.load(open("binary/cache/compile_commands.json", 'r'))
    except:
        self._content = []
    on_exit(self.__exit__)

@member(CompileCommandsLogger)
def __exit__(self):
    json.dump(self._content, open("binary/cache/compile_commands.json", 'w'), indent=4)

@member(CompileCommandsLogger)
def log_command(self, command, file):
    for entry in self._content:
        if entry["file"] == file:
            self._content.remove(entry)
    self._content.append({
        "directory": absolute_path('.'),
        "file"     : file,
        "command"  : ' '.join(command)
    })



compile_commands_logger = CompileCommandsLogger()
