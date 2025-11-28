from cppmakelib.file.file_system  import create_dir
from cppmakelib.utility.decorator import member

class CompileOutputLogger:
    def __init__  (self):         ...
    def log_output(self, output): ...

compile_output_logger = ...



@member(CompileOutputLogger)
def __init__(self):
    self._logged = False

@member(CompileOutputLogger)
def log_output(self, output):
    if not self._logged:
        create_dir("binary/cache")
        open("binary/cache/compile_output.txt", 'w').write(output)
        self._logged = True

compile_output_logger = CompileOutputLogger()