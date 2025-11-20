from cppmake.basic.config        import config
from cppmake.execution.run       import async_run
from cppmake.execution.scheduler import scheduler
from cppmake.system.all          import system
from cppmake.unit.source         import Source
from cppmake.utility.decorator   import member, once, syncable, trace, unique

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
    self.executable_file = f"binary/{config.type}/source/{self.name.replace('.', '/')}{system.executable_suffix}"
    self.import_source   = await Source.__anew__(Source, self.name)

@member(Executable)
@syncable
@once
@trace
async def async_execute(self):
    await self.import_source.async_compile()
    async with scheduler.schedule():
        await async_run(command=[self.executable_file])

