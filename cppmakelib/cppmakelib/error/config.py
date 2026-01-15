from cppmakelib.basic.exit        import on_terminate, rethrow_exception, current_exception
from cppmakelib.utility.color     import red, bold
from cppmakelib.utility.decorator import member
import sys

class ConfigError(Exception):
    def __init__     (self, message): ...
    def __terminate__():              ...
    def add_prefix   (self, prefix):  ...



@member(ConfigError)
def __init__(self, message):
    self.args = [f'{red(bold('fatal error:'))} {message}']
    on_terminate(ConfigError.__terminate__)

@member(ConfigError)
def __terminate__():
    try:
        rethrow_exception(current_exception())
    except ConfigError as error:
        print(error, file=sys.stderr)

@member(ConfigError)
def add_prefix(self, prefix):
    prefixed = ConfigError(*self.args)
    if not prefixed.args[0].startswith(prefix):
        prefixed.args = [prefix + '\n' + self.args[0]]
    return prefixed