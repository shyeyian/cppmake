from cppmake.basic.exit        import on_terminate, rethrow_exception, current_exception
from cppmake.utility.color     import red
from cppmake.utility.decorator import member
import sys

class ConfigError(Exception):
    def __init__     (self, message): ...
    def __terminate__():              ...
    def add_prefix   (self, prefix):  ...



@member(ConfigError)
def __init__(self, message):
    self.args = [message]
    on_terminate(ConfigError.__terminate__)

@member(ConfigError)
def __terminate__():
    try:
        rethrow_exception(current_exception())
    except ConfigError as error:
        print(f"{red("fatal error")}: {error}", file=sys.stderr)

@member(ConfigError)
def add_prefix(self, prefix):
    self.__init__(f"{prefix}\n{self}")
