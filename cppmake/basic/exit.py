import atexit
import sys

def on_exit          (func): ...
def on_terminate     (func): ...
def rethrow_exception(exc):  ...
def current_exception():     ...



def on_exit(func):
    atexit.register(func)

def on_terminate(func):
    global _terminate_hooked
    if func not in _terminate_hooked:
        _terminate_hooked |= {func}
        old_hook = sys.excepthook
        def new_hook(type, value, traceback):
            try:
                global _current_exception
                _current_exception = value
                func()
            except:
                old_hook(type, value, traceback)
        sys.excepthook = new_hook

def rethrow_exception(exc):
    raise exc

def current_exception():
    global _current_exception
    return _current_exception

_terminate_hooked = set()
_current_exception = None