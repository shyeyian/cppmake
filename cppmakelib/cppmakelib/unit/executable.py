from cppmakelib.execution.run       import async_run
from cppmakelib.execution.scheduler import scheduler
from cppmakelib.system.all          import system
from cppmakelib.unit.source         import Source
from cppmakelib.utility.decorator   import once, syncable, trace, unique

class Executable:
    @syncable
    @unique
    @trace
    async def __ainit__(self, name):
        self.name            = name
        self.executable_file = f'binary/source/{self.name}{system.executable_suffix}'
        self.require_source  = await Source.__anew__(Source, self.name)

    @syncable
    @once
    @trace
    async def async_execute(self):
        await self.require_source.async_compile()
        async with scheduler.schedule(scheduler.max):
            print(f'execute executable: {self.name}')
            await async_run(command=[self.executable_file])

