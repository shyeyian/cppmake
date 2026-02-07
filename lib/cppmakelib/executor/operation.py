def sync_wait     [T](task :      typing.Coroutine[typing.Any, typing.Any, T] ) -> T      : ...
def start_detached[T](task :      typing.Coroutine[typing.Any, typing.Any, T] ) -> None   : ...
def when_all      [T](tasks: list[typing.Coroutine[typing.Any, typing.Any, T]]) -> list[T]: ...
def when_any      [T](tasks: list[typing.Coroutine[typing.Any, typing.Any, T]]) -> T      : ...



import asyncio
import threading
import typing

def sync_wait[T](task: typing.Coroutine[typing.Any, typing.Any, T]) -> T:
    try:
        asyncio.get_running_loop()
        in_event_loop = True
    except RuntimeError:
        in_event_loop = False

    if not in_event_loop:
        return asyncio.run(task)
    else:
        value: T             | None = None
        error: BaseException | None = None
        def sync_func():
            try:
                nonlocal value
                value = asyncio.run(task)
            except BaseException as base_error:
                nonlocal error
                error = base_error
        thread = threading.Thread(target=sync_func)
        thread.start()
        thread.join()
        if error is None:
            value = typing.cast(T, value)
            return value
        else: 
            raise error

async def when_all[T](tasks: list[typing.Coroutine[typing.Any, typing.Any, T]]) -> list[T]:
    return await asyncio.gather(*tasks)