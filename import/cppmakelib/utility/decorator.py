import typing

def member     [S, **Ts, R](cls: type)                                                                                        -> typing.Callable[[typing.Callable[typing.Concatenate[S, Ts], R]], typing.Callable[typing.Concatenate[S, Ts], R]]: ...
def once       [S,       R](func: typing.Callable[[S], typing.Coroutine[typing.Any, typing.Any, R]])                          -> typing.Callable[[S], typing.Coroutine[typing.Any, typing.Any, R]]                                              : ...
@typing.overload
def relocatable[S, **Ts, R](func: typing.Callable[typing.Concatenate[S, Ts], R])                                              -> typing.Callable[typing.Concatenate[S, Ts], R]: ...
@typing.overload
def relocatable[S, **Ts, R](func: typing.Callable[typing.Concatenate[S, Ts], typing.Coroutine[typing.Any, typing.Any, R]])    -> typing.Callable[typing.Concatenate[S, Ts], typing.Coroutine[typing.Any, typing.Any, R]]: ...
def syncable   [   **Ts, R](func: typing.Callable[Ts, typing.Coroutine[typing.Any, typing.Any, R]])                           -> typing.Callable[Ts, typing.Coroutine[typing.Any, typing.Any, R]]                                               : ...
@typing.overload
def unique     [S, **Ts   ](func: typing.Callable[typing.Concatenate[S, Ts], None])                                           -> typing.Callable[typing.Concatenate[S, Ts], None]: ...
@typing.overload
def unique     [S, **Ts   ](func: typing.Callable[typing.Concatenate[S, Ts], typing.Coroutine[typing.Any, typing.Any, None]]) -> typing.Callable[typing.Concatenate[S, Ts], typing.Coroutine[typing.Any, typing.Any, None]]: ...



from cppmakelib.executor.operation import sync_wait
from cppmakelib.utility.filesystem import path
import asyncio
import inspect

# Every project has its own kind of shit mountain,
# and the main difference lies in where those mountains are placed.
# Some pile them up in plain sight, fully transparent to users
# (for example, C++ templates, which exposes every bit of the mess
# from their inner implementations but gains 'zero-cost abstraction'),
# while others prefer to hide them deep in a corner where no one can ever reach 
# (for example, the Python GIL).
#
# Here, in this project, we've gathered and neatly buried
# all our shit in the file below. :)

def member[S, **Ts, R](cls: type) -> typing.Callable[[typing.Callable[typing.Concatenate[S, Ts], R]], typing.Callable[typing.Concatenate[S, Ts], R]]:
    def memberizer(func: typing.Callable[typing.Concatenate[S, Ts], R]) -> typing.Callable[typing.Concatenate[S, Ts], R]:
        if inspect.isfunction(func):
            setattr(cls, func.__name__, func)
            return func
        elif isinstance(func, _MultiFunc):
            func = typing.cast(_MultiFunc[typing.Concatenate[S, Ts], R], func)
            for subfunc in func:
                memberizer(subfunc)
            return func
        else:
            assert False
    return memberizer

def once[S, R](func: typing.Callable[[S], typing.Coroutine[typing.Any, typing.Any, R]]) -> typing.Callable[[S], typing.Coroutine[typing.Any, typing.Any, R]]:
    assert inspect.iscoroutinefunction(func)
    async def once_func(self: S) -> R:
        if not hasattr      (self, f'_once_{func.__name__}'):
            setattr         (self, f'_once_{func.__name__}', asyncio.create_task(func(self)))
        return await getattr(self, f'_once_{func.__name__}')
    once_func.__name__ = func.__name__
    return once_func

def relocatable[S, **Ts, R](func: typing.Callable[typing.Concatenate[S, Ts], R | typing.Coroutine[typing.Any, typing.Any, R]]) -> typing.Callable[typing.Concatenate[S, Ts], R | typing.Coroutine[typing.Any, typing.Any, R]]:
    from cppmakelib.basic.context import context
    if inspect.isfunction(func) and not inspect.iscoroutinefunction(func):
        def relocatable_func(self: S, *args: Ts.args, **kwargs: Ts.kwargs) -> R:
            args, kwargs = _set_only_arg(args, kwargs, lambda path: f'{context.package.dir}/{path}')
            return func(self, *args, **kwargs)
        relocatable_func.__name__ = func.__name__
        return relocatable_func
    elif inspect.iscoroutinefunction(func):
        async def relocatable_func(self: S, *args: Ts.args, **kwargs: Ts.kwargs) -> R:
            args, kwargs = _set_only_arg(args, kwargs, lambda path: f'{context.package.dir}/{path}')
            return await func(self, *args, **kwargs)
        relocatable_func.__name__ = func.__name__
        return relocatable_func
    elif isinstance(func, _MultiFunc):
        func = typing.cast(_MultiFunc[typing.Concatenate[S, Ts], R | typing.Coroutine[typing.Any, typing.Any, R]], func)
        return _MultiFunc(*[relocatable(subfunc) for subfunc in func])
    else:
        assert False
        
def syncable[**Ts, R](func: typing.Callable[Ts, typing.Coroutine[typing.Any, typing.Any, R]]) -> typing.Callable[Ts, typing.Coroutine[typing.Any, typing.Any, R]]:
    if inspect.iscoroutinefunction(func):
        assert func.__name__.startswith('async_') or func.__name__.startswith('__a')
        def sync_func(*args: Ts.args, **kwargs: Ts.kwargs) -> R:
            return sync_wait(func(*args, **kwargs))
        sync_func.__name__ = func.__name__.removeprefix('async_') if func.__name__.startswith('async_') else func.__name__.replace('__a', '__')
        return _MultiFunc(func, sync_func)
    elif isinstance(func, _MultiFunc):
        func = typing.cast(_MultiFunc[Ts, typing.Coroutine[typing.Any, typing.Any, R]], func)
        return _MultiFunc(*[syncable(subfunc) for subfunc in func])
    else:
        assert False

def unique[S, **Ts](func: typing.Callable[typing.Concatenate[S, Ts], None | typing.Coroutine[typing.Any, typing.Any, None]]) -> typing.Callable[typing.Concatenate[S, Ts], None | typing.Coroutine[typing.Any, typing.Any, None]]:
    if inspect.isfunction(func) and not inspect.iscoroutinefunction(func):
        assert func.__name__ == '__init__'
        def unique_func(cls: type, *args: Ts.args, **kwargs: Ts.kwargs) -> None:
            arg = _get_only_arg(args, kwargs)
            if not hasattr        (cls, f'_unique'):
                setattr           (cls, f'_unique', {})
            if path not in getattr(cls, f'_unique').keys():
                getattr           (cls, f'_unique')[arg] = object.__new__(cls)
            return getattr        (cls, f'_unique')[arg]
        unique_func.__name__ = '__new__'
        return _MultiFunc(func, unique_func)
    elif inspect.iscoroutinefunction(func):
        assert func.__name__ == '__ainit__'
        async def unique_func(cls: type, *args: Ts.args, **kwargs: Ts.kwargs) -> None:
            arg = _get_only_arg(args, kwargs)
            if not hasattr        (cls, f'_unique'):
                setattr           (cls, f'_unique', {})
            if path not in getattr(cls, f'_unique').keys():
                getattr           (cls, f'_unique')[arg] = object.__new__(cls)
            await getattr         (cls, f'_unique')[arg].__ainit__(arg)
            return getattr        (cls, f'_unique')[arg]
        unique_func.__name__  = '__anew__'
        return _MultiFunc(func, unique_func)
    elif isinstance(func, _MultiFunc):
        return _MultiFunc(*[unique(subfunc) for subfunc in func])
    else:
        assert False

class _MultiFunc[**Ts, R]:
    def __init__(self, first: typing.Callable[Ts, R], *other: ...) -> None: ...
    def __call__(self, *args: Ts.args, **kwargs: Ts.kwargs)        -> R   : ...
    def __iter__(self)                                             -> typing.Iterator[typing.Callable[Ts, R] | typing.Any]: ...

    _functions: tuple[typing.Callable[Ts, R], ...]

@member(_MultiFunc)
def __init__[**Ts, R](self: _MultiFunc[Ts, R], first: typing.Callable[Ts, R], *other: ...) -> None:
    self._functions = (first, *other)

@member(_MultiFunc)
def __call__[**Ts, R](self: _MultiFunc[Ts, R], *args: Ts.args, **kwargs: Ts.kwargs) -> R:
    return self._functions[0](*args, **kwargs)

@member(_MultiFunc)
def __iter__[**Ts, R](self: _MultiFunc[Ts, R]) -> typing.Iterable[typing.Callable[Ts, R] | typing.Any]:
    return iter(self._functions)

def _get_only_arg(args: tuple[typing.Any, ...], kwargs: dict[str, typing.Any]) -> typing.Any:
    assert len(args) + len(kwargs) == 1
    if len(args) == 1:
        return args[0]
    elif len(kwargs) == 1:
        return list(kwargs.values())[0]
    else:
        assert False

def _set_only_arg(args: tuple[typing.Any, ...], kwargs: dict[str, typing.Any], operation: typing.Callable[[typing.Any], typing.Any]) -> typing.Any:
    assert len(args) + len(kwargs) == 1
    if len(args) == 1:
        return tuple(operation(args[0])), kwargs
    elif len(kwargs) == 1:
        return args, {list(kwargs.keys())[0]: operation(list(kwargs.values())[0])}
    else:
        assert False