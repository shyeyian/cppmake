from cppmakelib.error.subprocess    import SubprocessError
from cppmakelib.executor.run        import async_run
from cppmakelib.unit.binary         import Binary
from cppmakelib.utility.decorator   import member, once, syncable, unique
from cppmakelib.utility.filesystem  import path

class Executable(Binary):
    def           __new__  (cls,  file: path) -> Executable: ...
    def           __init__ (self, file: path) -> None      : ...
    def             execute(self)             -> None      : ...
    async def async_execute(self)             -> None      : ...
    def             test   (self)             -> None      : ...
    async def async_test   (self)             -> None      : ...



@member(Executable)
@unique
def __init__(self: Executable, file: path) -> None:
    super(Executable, self).__init__(file)
    
@member(Executable)
@syncable
@once
async def async_execute(self: Executable) -> None:
    try:
        await async_run(file=self.file)
    except SubprocessError:
        pass

@member(Executable)
@syncable
@once
async def async_test(self: Executable) -> None:
    await async_run(file=self.file)