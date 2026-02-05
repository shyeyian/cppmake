from cppmakelib.utility.color     import red, bold
from cppmakelib.utility.decorator import member

class SubprocessError(Exception):
    command  : list[str]
    exit_code: int
    stdout   : str
    stderr   : str
    def __init__(self, command: list[str], exit_code: int, stdout: str, stderr: str, command_printed: bool, stdout_printed: bool, stderr_printed: bool) -> None: ...
    def __str__ (self)                                                                                                                                  -> str: ...

    _command_printed: bool
    _stdout_printed : bool
    _stderr_printed : bool



@member(SubprocessError)
def __init__(
    self           : SubprocessError, 
    command        : list[str],
    exit_code      : int,
    stdout         : str,
    stderr         : str,
    command_printed: bool,
    stdout_printed : bool,
    stderr_printed : bool
) -> None:
    super(SubprocessError, self).__init__(command, exit_code, stdout, stderr)
    self.command          = command
    self.exit_code        = exit_code
    self.stdout           = stdout
    self.stderr           = stderr
    self._command_printed = command_printed
    self._stdout_printed  = stdout_printed
    self._stderr_printed  = stderr_printed

@member(SubprocessError)
def __str__(self: SubprocessError) -> str:
    command = ' '.join(self.command) if not self._command_printed else None
    stdout  = self.stdout if not self._stdout_printed else None
    stderr  = self.stderr if not self._stderr_printed else None
    message = '\n'.join([message for message in [command, stdout, stderr] if message is not None])
    return message
