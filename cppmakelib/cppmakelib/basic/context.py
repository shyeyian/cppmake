from cppmakelib.unit.package      import Package
from cppmakelib.utility.decorator import member
import typing

class Context:
    def switch(self, package: Package) -> typing.ContextManager[None]: ...
    package: Package 

    class _ContextManager:
        def __init__ (self, context: Context, package: Package)      -> None: ...
        def __enter__(self)                                          -> None: ...
        def __exit__ (self, *args: typing.Any, **kwargs: typing.Any) -> None: ...
        _context    : Context
        _old_package: Package
        _new_package: Package

context: Context



@member(Context)
def switch(self: Context, package: Package) -> typing.ContextManager[None]:
    return Context._ContextManager(self, package)

@member(Context._ContextManager)
def __init__(self: Context._ContextManager, context: Context, package: Package) -> None:
    self._context     = context
    self._old_package = context.package
    self._new_package = package

@member(Context._ContextManager)
def __enter__(self: Context._ContextManager) -> None:
    self._context.package = self._new_package

@member(Context._ContextManager)
def __exit__(self: Context._ContextManager, *args: typing.Any, **kwargs: typing.Any) -> None:
    self._context.package = self._old_package

context = Context()