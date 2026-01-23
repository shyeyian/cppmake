from cppmakelib.executor.operation  import sync_wait
import asyncio
import functools
import inspect
import threading
import typing

def member  [**Ts, R](cls: type)                                                -> typing.Callable[[typing.Callable[Ts, R]], None]   : ...
def once    [**Ts, R](func: typing.Callable[Ts, typing.Awaitable[R]])           -> typing.Callable[Ts, typing.Awaitable[R]]          : ...
def syncable[**Ts, R](func: typing.Callable[Ts, typing.Awaitable[R]])           -> typing.Callable[Ts, typing.Awaitable[R]]          : ...
def trace   [**Ts, R](func: typing.Callable[Ts, R])                             -> typing.Callable[Ts, R]                            : ...
def unique  [**Ts]   (func: typing.Callable[Ts, None | typing.Awaitable[None]]) -> typing.Callable[Ts, None | typing.Awaitable[None]]: ...

if typing.TYPE_CHECKING:
    @typing.overload
    def unique[**Ts](func: typing.Callable[Ts,                  None ]) -> typing.Callable[Ts,                  None ]: ...
    @typing.overload
    def unique[**Ts](func: typing.Callable[Ts, typing.Awaitable[None]]) -> typing.Callable[Ts, typing.Awaitable[None]]: ...

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

# def member[**Ts, R](cls: type) -> typing.Callable[[typing.Callable[Ts, R]], None]:
#     def attacher(func: typing.Callable[Ts, R]) -> None:
#         setattr(cls, func.__name__, func)
#     return attacher

# # unique走装饰class的路线，_MultiFunc总是长度为2，改名_SyncableFunc

# def syncable[**Ts, R](func: typing.Callable[Ts, typing.Awaitable[R]]) -> _SyncableFuncs[Ts, R]:
#     return _SyncableFuncs(func)

# def unique[**Ts](func: typing.Callable[Ts, typing.Awaitable[None]]) -> _UniqueFuncs[Ts]:
#     return _UniqueFuncs(func)

# class _SyncableFuncs[**Ts, R]:
#     def __init__   (self, funcs: list[typing.Callable[Ts, R | typing.Awaitable[R]]]) -> None                                   : ...
#     def __iter__   (self)                                      -> typing.Iterable[typing.Callable[Ts, R | typing.Awaitable[R]]]: ...
#     def __getitem__(self, index: int)                          -> typing.Callable[Ts, R | typing.Awaitable[R]]                 : ...
#     def __call__   (self, *args: Ts.args, **kwargs: Ts.kwargs) -> R | typing.Awaitable[R]                                      : ...

#     _sync_func : typing.Callable[Ts, R]
#     _async_func: typing.Callable[Ts, typing.Awai]

#     _funcs: list[typing.Callable[..., typing.Any]]

# class _UniqueFuncs[**Ts]:
#     ...




#     assert func.__name__.startswith('async_') or func.__name__.startswith('__a') # Should have pre-declaraed the corresponding methods.
#     def sync_func(*args: Ts.args, **kwargs: Ts.kwargs) -> R:
#         value: R | None = None
#         error: Exception | None = None
#         def target():
#             nonlocal value
#             nonlocal error
#             try:
#                 value = sync_wait(func(*args, **kwargs))
#             except Exception as exception:
#                 error = exception
#         thread = threading.Thread(target=target)
#         thread.start()
#         thread.join()
#         if value is not None:
#             return value
#         elif error is not None:
#             raise error
#         else:
#             assert False
#     if func.__name__.startswith('async_'):
#         sync_func.__name__ = func.__name__[6:]
#     elif func.__name__.startswith('__a'):
#         sync_func.__name__ = func.__name__[:2] + func.__name__[3:]
#     else:
#         assert False
#     return _SyncableFunc(func, sync_func)

# @member(_MultiFunc)
# def __init__[**Ts, R](self: _MultiFunc[Ts, R], funcs: list[typing.Callable[Ts, R | typing.Awaitable[R]]]) -> None:
#     self._funcs = funcs
#     for subfunc in self._funcs[1:]:
#         setattr(inspect.getmodule(subfunc), subfunc.__name__, subfunc)

# @member(_MultiFunc)
# def __iter__[**Ts, R](self: _MultiFunc[Ts, R]) -> typing.Iterable[typing.Callable[..., typing.Any]]:
#     return iter(self._funcs)

# @member(_MultiFunc)
# def __getitem__[**Ts, R](self: _MultiFunc[Ts, R], index: int):
#     return self._funcs[index]

# @member(_MultiFunc)
# def __call__[**Ts, R](self: _MultiFunc[Ts, R], *args: Ts.args, **kwargs: Ts.kwargs) -> R | typing.Awaitable[R]:
#     return self._funcs[0](*args, **kwargs)


# def once(func):
#     assert inspect.iscoroutinefunction(func)
#     @functools.wraps(func)
#     async def once_func(self, *args): # No kwargs
#         if not         hasattr(self, f'_once_{func.__name__}'):
#                        setattr(self, f'_once_{func.__name__}', {})
#         if args not in getattr(self, f'_once_{func.__name__}').keys():
#                        getattr(self, f'_once_{func.__name__}')[args] = asyncio.create_task(func(self, *args))
#         return await   getattr(self, f'_once_{func.__name__}')[args]
#     return once_func

# def syncable(func):
#     # Do not syncable a method when existing a same-named global function.
#     # For example, when we have 'run(command=...)', do not define 'class Executable: @syncable async_run(self)', use 'async_execute' instead.
#     if type(func) != _MultiFunc:
#         assert inspect.iscoroutinefunction(func)
#         assert func.__name__.startswith('async_') or func.__name__.startswith('__a') # Should have pre-declaraed the corresponding methods.
#         @functools.wraps(func)
#         def sync_func(*args, **kwargs):
#             value = None
#             error = None
#             def target():
#                 nonlocal value
#                 nonlocal error
#                 try:
#                     value = sync_wait(func(*args, **kwargs))
#                 except Exception as suberror:
#                     error = suberror
#                 except KeyboardInterrupt as suberror:
#                     error = suberror
#                 except:
#                      raise
#             thread = threading.Thread(target=target)
#             thread.start()
#             thread.join()
#             if error is None:
#                 return value
#             else:
#                 raise error
#         sync_func.__name__ = func.__name__.removeprefix('async_') if func.__name__.startswith('async_') else \
#                              func.__name__.replace('__a', '__')   if func.__name__.startswith('__a')    else \
#                              assert_(False)
#         return _MultiFunc([func, sync_func])
#     else:
#         results = [func_or_sync_func for subfunc in func for func_or_sync_func in syncable(subfunc)]
#         return _MultiFunc(results)

# def trace(func):
#     assert inspect.isfunction(func)
#     if not inspect.iscoroutinefunction(func):
#         @functools.wraps(func)
#         def trace_func(self, *args, **kwargs):
#             try:
#                 return func(self, *args, **kwargs)
#             except Exception as error:
#                 if hasattr(error, 'add_prefix'):
#                      raise error.add_prefix(f'In {type(self).__qualname__.lower()} {self.name}:')
#                 else:
#                      raise error
#         return trace_func
#     else:
#         @functools.wraps(func)
#         async def trace_func(self, *args, **kwargs):
#             try:
#                 return await func(self, *args, **kwargs)
#             except Exception as error:
#                 if hasattr(error, 'add_prefix'):
#                      raise error.add_prefix(f'In {type(self).__qualname__.lower()} {self.name}:')
#                 else:
#                      raise error
#     return trace_func
    
# def unique(func):
#     assert inspect.isfunction(func)
#     assert func.__name__ == '__ainit__'
#     @functools.wraps(func)
#     async def unique_anew(cls, *args, **kwargs):
#         if not hasattr(cls, '_pool'):
#                setattr(cls, '_pool', {})
#         if args in cls._pool.keys():
#             self = cls._pool[args]
#         else:
#             self = super(cls, cls).__new__(cls)
#             cls._pool[args] = self
#         await func(self, *args, **kwargs)
#         return self
#     unique_anew.__name__ = '__anew__'
#     return _MultiFunc([func, once(unique_anew)])
