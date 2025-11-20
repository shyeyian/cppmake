from cppmake.basic.exit        import on_terminate, rethrow_exception, current_exception
from cppmake.utility.decorator import member
import sys

class SubprocessError(Exception):
    def __init__     (self, code, stderr, is_stderr_printed): ...
    def __terminate__():                                      ...



@member(SubprocessError)
def __init__(self, code, stderr, is_stderr_printed):
    self.args = [stderr]
    self._code = code
    self._is_stderr_printed = is_stderr_printed
    on_terminate(SubprocessError.__terminate__)

@member(SubprocessError)
def __terminate__():
    try:
        rethrow_exception(current_exception())
    except SubprocessError as error:
        if not error._is_stderr_printed:
            print(error, file=sys.stderr)