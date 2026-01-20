import asyncio
import typing

def sync_wait     [T](task :      typing.Coroutine[typing.Any, typing.Any, T] ) -> T      : ...
def start_detached[T](task :      typing.Coroutine[typing.Any, typing.Any, T] ) -> None   : ...
def when_all      [T](tasks: list[typing.Coroutine[typing.Any, typing.Any, T]]) -> list[T]: ...
def when_any      [T](tasks: list[typing.Coroutine[typing.Any, typing.Any, T]]) -> T      : ...



def sync_wait[T](task: typing.Coroutine[typing.Any, typing.Any, T]) -> T:
    return asyncio.run(task)

async def when_all[T](tasks: list[typing.Coroutine[typing.Any, typing.Any, T]]) -> list[T]:
    return await asyncio.gather(*tasks)