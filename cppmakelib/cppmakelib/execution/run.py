from cppmakelib.basic.config            import config
from cppmakelib.error.subprocess        import SubprocessError
from cppmakelib.execution.operation     import when_all
from cppmakelib.execution.scheduler     import Scheduler
from cppmakelib.file.file_system        import Path
from cppmakelib.logger.compile_commands import compile_commands_logger
from cppmakelib.utility.decorator       import syncable
import asyncio
import sys
import typing

def             run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, return_stdout: bool = False, return_stderr: bool = False) -> None | str | tuple[str, str]: ...
async def async_run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, return_stdout: bool = False, return_stderr: bool = False) -> None | str | tuple[str, str]: ...

if typing.TYPE_CHECKING:
    @typing.overload
    def             run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[False] = False) -> None: ...
    @typing.overload
    def             run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[False] = False) -> str: ...
    @typing.overload
    def             run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[True]         ) -> str: ...
    @typing.overload
    def             run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[True]         ) -> tuple[str, str]: ...
    @typing.overload
    async def async_run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[False] = False) -> None: ...
    @typing.overload
    async def async_run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[False] = False) -> str: ...
    @typing.overload
    async def async_run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[True]         ) -> str: ...
    @typing.overload
    async def async_run(file: Path, args: list[str] = [], cwd: Path = Path('.'), print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[True]         ) -> tuple[str, str]: ...



_internal_scheduler = Scheduler(config.parallel)

@syncable
async def async_run(
    file          : Path,
    args          : list[str] = [], 
    cwd           : Path      = Path('.'), 
    print_command : bool      = config.verbose,
    print_stdout  : bool      = config.verbose,
    print_stderr  : bool      = True,
    return_stdout : bool      = False,
    return_stderr : bool      = False,
) -> None | str:
    async with _internal_scheduler.schedule():
        proc = await asyncio.subprocess.create_subprocess_exec(
            file, 
            *args,
            cwd   =cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        assert isinstance(proc.stdout, asyncio.StreamReader)
        assert isinstance(proc.stderr, asyncio.StreamReader)
        async def read(stream: asyncio.StreamReader, tee: typing.TextIO | None) -> str:
            text = ''
            while True:
                line = await stream.readline()
                if not stream.at_eof():
                    line = line.decode()
                    text += line
                    print(line, end='', file=tee) if tee is not None else None
                else:
                    break
            return text
        stdout, stderr = await when_all([
            read(stream=proc.stdout, tee=sys.stdout if print_stdout else None),
            read(stream=proc.stderr, tee=sys.stderr if print_stderr else None)
        ])
        code = await proc.wait()
        if code == 0:
            if return_stdout:
                return stdout
            elif return_stderr:
                return stderr
            else:
                return None
        else:
            raise SubprocessError(stderr=stderr, is_stderr_printed=print_stderr, code=code)
