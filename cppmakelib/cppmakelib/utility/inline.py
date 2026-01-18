from cppmakelib.utility.template import template
import typing

def assert_(value: bool, message: str | None = None):
    if message is None:
        assert value
    else:
        assert value, message

def raise_(error: Exception):
    raise error

def value_or(func: typing.Callable[[], template], fallback: template):
    try:
        return func()
    except:
        return fallback