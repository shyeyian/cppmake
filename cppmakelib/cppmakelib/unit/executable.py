from cppmakelib.basic.config        import config
from cppmakelib.execution.run       import async_run
from cppmakelib.execution.scheduler import scheduler
from cppmakelib.system.all          import system
from cppmakelib.unit.source         import Source
from cppmakelib.utility.decorator   import member, once, syncable, trace, unique

class Executable:
    def           __init__ (self, name): ...
    async def     __ainit__(self, name): ...
    def             execute(self):       ...
    async def async_execute(self):       ...

@member(Executable)
@syncable
@once
@trace
async def __ainit__(self, name):
    self.name            = name
    self.executable_file = f"binary/source/{self.name}{system.executable_suffix}"
    self.import_source   = await Source.__anew__(Source, self.name)

@member(Executable)
@syncable
@once
@trace
async def async_execute(self):
    await self.import_source.async_compile()
    async with scheduler.schedule(scheduler.max):
        print(f"execute executable: {self.name}")
        await async_run(command=[self.executable_file])

