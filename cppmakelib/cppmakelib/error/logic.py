from cppmakelib.basic.exit        import on_terminate, rethrow_exception, current_exception
from cppmakelib.utility.color     import red, bold
from cppmakelib.utility.decorator import member
import sys

class LogicError(Exception):
    def __init__     (self, message): ...
    def __terminate__():              ...
    def add_prefix   (self, prefix):  ...



@member(LogicError)
def __init__(self, message):
    self.args = [f'{red(bold('fatal error:'))} {message}']
    on_terminate(LogicError.__terminate__)

@member(LogicError)
def __terminate__():
    try:
        rethrow_exception(current_exception())
    except LogicError as error:
        print(error, file=sys.stderr)

@member(LogicError)
def add_prefix(self, prefix):
    prefixed = LogicError(*self.args)
    if not prefixed.args[0].startswith(prefix):
        prefixed.args = [prefix + '\n' + self.args[0]]
    return prefixed
