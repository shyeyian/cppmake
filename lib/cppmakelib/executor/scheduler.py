from cppmakelib.basic.config      import config
from cppmakelib.utility.decorator import member
import asyncio
import typing

class Scheduler:
    def __init__(self, value: int = config.parallel) -> None                            : ...
    def schedule(self, value: int = 1)               -> typing.AsyncContextManager[None]: ...
    max: int

    class _ContextManager:
        def       __init__  (self, scheduler: Scheduler, value: int)        -> None: ...
        async def __aenter__(self)                                          -> None: ...
        async def __aexit__ (self, *args: typing.Any, **kwargs: typing.Any) -> None: ...
        _scheduler: Scheduler
        _value    : int
    class _NotifyFailedError(RuntimeError):
        pass
    async def _acquire   (self, value: int = 1) -> None: ...
    def       _release   (self, value: int = 1) -> None: ...
    def       _notify_one(self)                 -> None: ...
    _value  : int
    _waiters: dict[asyncio.Future[None], int]

scheduler: Scheduler



@member(Scheduler)
def __init__(self: Scheduler, value: int = config.parallel) -> None:
    assert value >= 0
    self.max      = value
    self._value   = value
    self._waiters = {}

@member(Scheduler)
def schedule(self: Scheduler, value: int = 1) -> typing.AsyncContextManager[None]:
    return Scheduler._ContextManager(self, value)

@member(Scheduler._ContextManager)
def __init__(self: Scheduler._ContextManager, scheduler: Scheduler, value: int):
    self._scheduler = scheduler
    self._value     = value

@member(Scheduler._ContextManager)
async def __aenter__(self: Scheduler._ContextManager) -> None:
    return await self._scheduler._acquire(self._value)

@member(Scheduler._ContextManager)
async def __aexit__(self: Scheduler._ContextManager, *args: typing.Any, **kwargs: typing.Any) -> None:
    self._scheduler._release(self._value)

@member(Scheduler)
async def _acquire(self: Scheduler, value: int = 1) -> None:
    if self._value >= value and all(not waiter.cancelled() for waiter in self._waiters.keys()):
        self._value -= value
        return
    future = asyncio.get_event_loop().create_future()
    self._waiters[future] = value
    try:
        try:
            await future
        finally:
            self._waiters.pop(future)
    except asyncio.CancelledError:
        if future.done() and not future.cancelled():
            self._value += value
        raise
    finally:
        while self._value > 0:
            try:
                self._notify_one()
            except Scheduler._NotifyFailedError:
                break
    return

@member(Scheduler)
def _release(self: Scheduler, value: int = 1) -> None:
    self._value += value
    self._notify_one()

@member(Scheduler)
def _notify_one(self: Scheduler) -> None:
    for future in self._waiters.keys():
        if not future.done() and self._value >= self._waiters[future]:
            self._value -= self._waiters[future]
            future.set_result(None)
            return
    raise Scheduler._NotifyFailedError('no waiters notified')

scheduler = Scheduler()