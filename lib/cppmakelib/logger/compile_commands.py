from cppmakelib.utility.decorator  import member
from cppmakelib.utility.filesystem import absolute_path, create_dir, parent_dir, path
import json
import typing

class CompileCommandsLogger:
    def __init__(self) -> None: ...
    def __del__ (self) -> None: ...
    def log(self, file: path, command: list[str]) -> None: ...

    _file   : path
    _content: typing.Any

compile_commands_logger: CompileCommandsLogger



@member(CompileCommandsLogger)
def __init__(self: CompileCommandsLogger) -> None:
    self._file = '.cppmake/utility/compile_commands.json'
    try:
        self._content = json.load(open(self._file, 'r'))
    except:
        self._content = []

@member(CompileCommandsLogger)
def __del__(self: CompileCommandsLogger) -> None:
    create_dir(parent_dir(self._file))
    json.dump(self._content, open(self._file, 'w'), indent=4)

@member(CompileCommandsLogger)
def log(self: CompileCommandsLogger, file: path, command: list[str]) -> None:
    for entry in self._content:
        if entry['file'] == file:
            self._content.remove(entry)
    self._content.append({
        'directory': absolute_path('.'),
        'file'     : file,
        'command'  : ' '.join(command)
    })

compile_commands_logger = CompileCommandsLogger()
