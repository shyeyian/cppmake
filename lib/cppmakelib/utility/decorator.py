from cppmakelib.executor.operation import sync_wait
from cppmakelib.utility.filesystem import path, relative_path
import asyncio
import inspect
import typing

def implement  [**Ts, R](func: typing.Callable[Ts, R])                                                            -> typing.Callable[Ts, R]                                                           : ...
def member              (cls: type)                                                                               -> typing.Callable[[typing.Callable[..., typing.Any]], None]                        : ...
def once       [S, R]   (func: typing.Callable[[S], typing.Coroutine[typing.Any, typing.Any, R]])                 -> typing.Callable[[S], typing.Coroutine[typing.Any, typing.Any, R]]                : ...
def relocatable[S, R]   (func: typing.Callable[[S, path], R])                                                     -> typing.Callable[[S, path], R]                                                    : ...
def syncable   [**Ts, R](func: typing.Callable[Ts, typing.Coroutine[typing.Any, typing.Any, R]])                  -> typing.Callable[Ts, typing.Coroutine[typing.Any, typing.Any, R]]                 : ...
def unique     [S]      (func: typing.Callable[[S, path], None | typing.Coroutine[typing.Any, typing.Any, None]]) -> typing.Callable[[S, path], None | typing.Coroutine[typing.Any, typing.Any, None]]: ...

if typing.TYPE_CHECKING:
    @typing.overload
    def unique[S](func: typing.Callable[[S, path],                                          None ]) -> typing.Callable[[S, path],                                          None ]: ...
    @typing.overload
    def unique[S](func: typing.Callable[[S, path], typing.Coroutine[typing.Any, typing.Any, None]]) -> typing.Callable[[S, path], typing.Coroutine[typing.Any, typing.Any, None]]: ...

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

def member(cls: type) -> typing.Callable[[typing.Callable[..., typing.Any]], None]:
    def memberizer(func: typing.Callable[..., typing.Any]) -> None:
        if inspect.isfunction(func):
            setattr(cls, func.__name__, func)
        elif isinstance(func, _MultiFunc):
            for subfunc in func.functions:
                memberizer(subfunc)
        else:
            assert False
    return memberizer

def once[S, R](func: typing.Callable[[S], typing.Coroutine[typing.Any, typing.Any, R]]) -> typing.Callable[[S], typing.Coroutine[typing.Any, typing.Any, R]]:
    async def once_func(self: S) -> R:
        if not hasattr      (self, f'_once_{func.__name__}'):
            setattr         (self, f'_once_{func.__name__}', asyncio.create_task(func(self)))
        return await getattr(self, f'_once_{func.__name__}')
    once_func.__name__ = func.__name__
    return once_func

def relocatable[S, R](func: typing.Callable[[S, path], R]) -> typing.Callable[[S, path], R]:
    def relocatable_func(self: S, path: path) -> R:
        from cppmakelib.basic.context import context
        relocated_path = relative_path(from_path='.', to_path=f'{context.package.dir}/{path}')
        return func(self, relocated_path)
    relocatable_func.__name__ = func.__name__
    return relocatable_func

def syncable[**Ts, R](func: typing.Callable[Ts, typing.Coroutine[typing.Any, typing.Any, R]]) -> typing.Callable[Ts, typing.Coroutine[typing.Any, typing.Any, R]]:
    if inspect.isfunction(func):
        assert func.__name__.startswith('async_') or func.__name__.startswith('__a')
        def sync_func(*args: Ts.args, **kwargs: Ts.kwargs) -> R:
            return sync_wait(func(*args, **kwargs))
        sync_func.__name__ = func.__name__.removeprefix('async_') if func.__name__.startswith('async_') else func.__name__.replace('__a', '__')
        return _MultiFunc(func, sync_func)
    elif isinstance(func, _MultiFunc):
        return _MultiFunc[Ts, typing.Coroutine[typing.Any, typing.Any, R]](*[syncable(subfunc) for subfunc in func.functions])
    else:
        assert False

def unique[S](func: typing.Callable[[S, path], None | typing.Coroutine[typing.Any, typing.Any, None]]) -> typing.Callable[[S, path], None | typing.Coroutine[typing.Any, typing.Any, None]]:
    if inspect.isfunction(func) and not inspect.iscoroutinefunction(func):
        assert func.__name__ == '__init__'
        def unique_func(cls: type, path: path):
            if not hasattr        (cls, f'_unique'):
                setattr           (cls, f'_unique', {})
            if path not in getattr(cls, f'_unique').keys():
                getattr           (cls, f'_unique')[path] = super(cls, cls).__new__(cls)
            return getattr        (cls, f'_unique')[path]
        unique_func.__name__ = '__new__'
        return _MultiFunc(func, unique_func)
    elif inspect.iscoroutinefunction(func):
        assert func.__name__ == '__ainit__'
        async def unique_func(cls: type, path: path):
            if not hasattr        (cls, f'_unique'):
                setattr           (cls, f'_unique', {})
            if path not in getattr(cls, f'_unique').keys():
                getattr           (cls, f'_unique')[path] = super(cls, cls).__new__(cls)
            await getattr         (cls, f'_unique')[path].__ainit__(path)
            return getattr        (cls, f'_unique')[path]
        unique_func.__name__  = '__anew__'
        return _MultiFunc(func, unique_func)
    elif isinstance(func, _MultiFunc):
        return _MultiFunc(*[unique(subfunc) for subfunc in func.functions])
    else:
        assert False

class _MultiFunc[**Ts, R]:
    def __init__ (self, first: typing.Callable[Ts, R], *other: ...) -> None: ...
    def __call__ (self, *args: Ts.args, **kwargs: Ts.kwargs)        -> R   : ...
    functions: tuple[typing.Callable[Ts, R], ...]

@member(_MultiFunc)
def __init__[**Ts, R](self: _MultiFunc[Ts, R], first: typing.Callable[Ts, R], *other: ...) -> None:
    self.functions = (first, *other)

@member(_MultiFunc)
def __call__[**Ts, R](self: _MultiFunc[Ts, R], *args: Ts.args, **kwargs: Ts.kwargs) -> R:
    return self.functions[0](*args, **kwargs)
