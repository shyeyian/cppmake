from cppmake.execution.operation import sync_wait
from cppmake.utility.inline      import assert_
import asyncio
import inspect
import threading

def member  (cls ): ...
def namable (func): ...
def once    (func): ...
def syncable(func): ...
def trace   (func): ...
def unique  (cls ): ...



# Every project has its own kind of shit mountain,
# and the main difference lies in where those mountains are placed.
# Some pile them up in plain sight, fully transparent to users
# (for example, C++ templates, which "zero-cost" expose every bit
# of mess from their inner implementations),
# while others prefer to hide them deep in a corner
# where no one can ever reach (for example, the Python GIL).
#
# Here, in this project, we've gathered and neatly buried
# all our shit in the file below. :)

def member(cls):
    assert inspect.isclass(cls)
    def memberizer(func):
        if type(func) != _MultiFunc:
            assert hasattr(cls, func.__name__) or func.__name__.startswith("_") # Private functions which starts with '_' are not required to be pre-declared in class.
            setattr(cls, func.__name__, func)
        else:
            for subfunc in func:
                memberizer(subfunc)
    return memberizer

def namable(func):
    if type(func) != _MultiFunc:
        assert inspect.iscoroutinefunction(func)
        async def namable_func(arg1, name=None, **kwargs):
            cls = arg1 if type(arg1) == type else type(arg1)
            if cls.__qualname__.lower() == "module" or cls.__qualname__.lower() == "source": # Yes, this is fully shit, but we just make it work.
                assert (name is not None and len(kwargs) == 0) or (name is None and len(kwargs) == 1 and "file" in kwargs.keys())
                file = kwargs["file"] if "file" in kwargs else None
                return await func(arg1, name,       cls.      _name_to_file(name))       if name is not None and file is     None and hasattr(cls,       "_name_to_file") else \
                       await func(arg1, name, await cls._async_name_to_file(name))       if name is not None and file is     None and hasattr(cls, "_async_name_to_file") else \
                       await func(arg1,             cls.      _file_to_name(file), file) if name is     None and file is not None and hasattr(cls,       "_file_to_name") else \
                       await func(arg1,       await cls._async_file_to_name(file), file) if name is     None and file is not None and hasattr(cls, "_async_file_to_name") else \
                       assert_(False)
            elif cls.__qualname__.lower() == "package":
                assert (name is not None and len(kwargs) == 0) or (name is None and len(kwargs) == 1 and "dir" in kwargs.keys())
                dir = kwargs["dir"] if "dir" in kwargs else None
                return await func(arg1, name,       cls.      _name_to_dir(name))     if name is not None and dir is     None and hasattr(cls,       "_name_to_dir") else \
                       await func(arg1, name, await cls._async_name_to_dir(name))     if name is not None and dir is     None and hasattr(cls, "_async_name_to_dir") else \
                       await func(arg1,             cls.      _dir_to_name(dir), dir) if name is     None and dir is not None and hasattr(cls,       "_dir_to_name") else \
                       await func(arg1,       await cls._async_dir_to_name(dir), dir) if name is     None and dir is not None and hasattr(cls, "_async_dir_to_name") else \
                       assert_(False)
            else:
                assert False
        namable_func.__name__ = func.__name__
        return namable_func
    else:
        return _MultiFunc([namable(subfunc) for subfunc in func])

def once(func):
    assert inspect.iscoroutinefunction(func)
    async def once_func(self, *args): # No kwargs
        if not         hasattr(self, f"_once_{func.__name__}"):
                       setattr(self, f"_once_{func.__name__}", {})
        if args not in getattr(self, f"_once_{func.__name__}").keys():
                       getattr(self, f"_once_{func.__name__}")[args] = asyncio.create_task(func(self, *args))
        return await   getattr(self, f"_once_{func.__name__}")[args]
    once_func.__name__ = func.__name__
    return once_func

def syncable(func):
    if type(func) != _MultiFunc:
        assert inspect.iscoroutinefunction(func)
        assert func.__name__.startswith("async_") or func.__name__.startswith("__a") # Should have pre-declaraed the corresponding methods.
        def sync_func(*args, **kwargs):
            value = None
            error = None
            def target():
                nonlocal value
                nonlocal error
                try:
                    value = sync_wait(func(*args, **kwargs))
                except Exception as suberror:
                    error = suberror
                except KeyboardInterrupt as suberror:
                    error = suberror
            thread = threading.Thread(target=target)
            thread.start()
            thread.join()
            if error is None:
                return value
            else:
                raise error
        sync_func.__name__ = func.__name__.removeprefix("async_") if func.__name__.startswith("async_") else \
                             func.__name__.replace('__a', '__')   if func.__name__.startswith("__a")    else \
                             assert_(False)
        return _MultiFunc([func, sync_func])
    else:
        results = [func_or_sync_func for subfunc in func for func_or_sync_func in syncable(subfunc)]
        return _MultiFunc(results)

def trace(func):
    assert inspect.isfunction(func)
    if not inspect.iscoroutinefunction(func):
        def trace_func(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as error:
                if hasattr(error, "add_prefix"):
                    raise error.add_prefix(f"In {type(self).__qualname__.lower()}")
                else:
                    raise error
        return trace_func
    else:
        async def trace_func(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except Exception as error:
                if hasattr(error, "add_prefix"):
                    raise error.add_prefix(f"In {type(self).__qualname__.lower()}")
                else:
                    raise error
    trace_func.__name__ = func.__name__
    return trace_func
    
def unique(func):
    assert inspect.isfunction(func)
    assert func.__name__ == "__ainit__"
    async def unique_anew(cls, *args, **kwargs):
        if not hasattr(cls, "_pool"):
               setattr(cls, "_pool", {})
        if args in cls._pool.keys():
            self = cls._pool[args]
        else:
            self = super(cls, cls).__new__(cls)
            cls._pool[args] = self
        await func(self, *args, **kwargs)
        return self
    unique_anew.__name__ = "__anew__"
    return _MultiFunc([func, unique_anew])

class _MultiFunc:
    def __init__(self, funcs):
        assert type(funcs) == list
        self._funcs = funcs
        for subfunc in self._funcs[1:]:
            setattr(__import__(subfunc.__module__), subfunc.__name__, subfunc)
    def __iter__(self):
        return iter(self._funcs)
    def __getitem__(self, index):
        return self._funcs[index]
    async def __call__(self, *args, **kwargs):
        return await self._funcs[0](*args, **kwargs)