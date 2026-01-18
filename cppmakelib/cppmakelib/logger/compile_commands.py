from cppmakelib.file.file_system  import absolute_path, parent_path, create_dir
from cppmakelib.utility.decorator import member
import json

class CompileCommandsLogger:
    def __init__(self):
        self.file = 'binary/.cache/compile_commands.json'
        try:
            self._content = json.load(open(self.file, 'r'))
        except:
            self._content = []

    def __del__(self):
        if len(self._content) > 0:
            create_dir(parent_path(self.file))
            json.dump(self._content, open(self.file, 'w'), indent=4)

    def log_command(self, command, file):
        for entry in self._content:
            if entry['file'] == file:
                self._content.remove(entry)
        self._content.append({
            'directory': absolute_path('.'),
            'file'     : file,
            'command'  : ' '.join(command)
        })



compile_commands_logger = CompileCommandsLogger()
