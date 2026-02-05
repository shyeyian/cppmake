from cppmakelib.utility.filesystem import absolute_path, path
from cppmakelib.utility.decorator  import member
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
    self._file = 'binary/cache/compile_commands.json'
    with open(self._file, 'r') as reader:
        try:
            self._content = json.load(reader)
        except:
            self._content = []

@member(CompileCommandsLogger)
def __del__(self: CompileCommandsLogger) -> None:
    with open(self._file, 'w') as writer:
        json.dump(self._content, writer, indent=4)

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
