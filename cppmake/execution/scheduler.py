from cppmake.basic.config      import config
from cppmake.utility.decorator import member
import asyncio

class Scheduler:
    def __init__(self, value=config.parallel): ...
    def schedule(self, weight=1):              ...

scheduler = ...



@member(Scheduler)
def __init__(self, value=config.parallel):
    assert value >= 0
    self.max      = value
    self._value   = value
    self._waiters = {}

@member(Scheduler)
def schedule(self, weight=1):
    return Scheduler._Context(self, weight)

@member(Scheduler)
async def _acquire(self, weight=1):
    if self._value >= weight and all(waiter.cancelled() for waiter in self._waiters.keys()):
        self._value -= weight
        return
    future = asyncio.get_event_loop().create_future()
    self._waiters[future] = weight
    try:
        try:
            await future
        finally:
            self._waiters.pop(future)
    except asyncio.CancelledError:
        if future.done() and not future.cancelled():
            self._value += weight
        raise
    finally:
        while self._value > 0:
            woke = self._notify_one()
            if not woke:
                break
    return

@member(Scheduler)
def _release(self, weight=1):
    self._value += weight
    self._notify_one()

@member(Scheduler)
def _notify_one(self):
    for future in self._waiters.keys():
        if not future.done() and self._value >= self._waiters[future]:
            self._value -= self._waiters[future]
            future.set_result(True)
            return True
    return False

@member(Scheduler)
class _Context:
    def       __init__  (self, scheduler, weight): ...
    async def __aenter__(self):                    ...
    async def __aexit__ (self, *args):             ...

@member(Scheduler._Context)
def __init__(self, scheduler, weight):
    self._scheduler = scheduler
    self._weight    = weight

@member(Scheduler._Context)
async def __aenter__(self):
    return await self._scheduler._acquire(self._weight)

@member(Scheduler._Context)
async def __aexit__(self, *args):
    self._scheduler._release(self._weight)

scheduler = Scheduler()