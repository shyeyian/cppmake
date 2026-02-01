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
        context    : Context
        old_package: Package
        new_package: Package

context: Context



@member(Context)
def switch(self: Context, package: Package) -> typing.ContextManager[None]:
    return Context._ContextManager(self, package)

@member(Context._ContextManager)
def __init__(self: Context._ContextManager, context: Context, package: Package) -> None:
    self.context     = context
    self.old_package = context.package
    self.new_package = package

@member(Context._ContextManager)
def __enter__(self: Context._ContextManager) -> None:
    self.context.package = self.new_package

@member(Context._ContextManager)
def __exit__(self: Context._ContextManager, *args: typing.Any, **kwargs: typing.Any) -> None:
    self.context.package = self.old_package

context = Context()