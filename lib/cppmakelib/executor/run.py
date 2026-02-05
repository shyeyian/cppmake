from cppmakelib.basic.config            import config
from cppmakelib.error.subprocess        import SubprocessError
from cppmakelib.executor.operation      import when_all
from cppmakelib.executor.scheduler      import Scheduler
from cppmakelib.utility.filesystem      import path
from cppmakelib.logger.compile_commands import compile_commands_logger
from cppmakelib.logger.make_progress    import make_progress_logger``
from cppmakelib.utility.decorator       import syncable
import asyncio
import sys
import typing

def             run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, return_stdout: bool = False, return_stderr: bool = False) -> None | str | tuple[str, str]: ...
async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, return_stdout: bool = False, return_stderr: bool = False) -> None | str | tuple[str, str]: ...

if typing.TYPE_CHECKING:
    @typing.overload
    def             run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[False] = False) -> None           : ...
    @typing.overload
    def             run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[True])          -> str            : ...
    @typing.overload
    def             run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[False] = False) -> str            : ...
    @typing.overload
    def             run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[True])          -> tuple[str, str]: ...
    @typing.overload
    async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[False] = False) -> None           : ...
    @typing.overload
    async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[True])          -> str            : ...
    @typing.overload
    async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[False] = False) -> str            : ...
    @typing.overload
    async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[True])          -> tuple[str, str]: ...



_internal_scheduler = Scheduler(config.parallel)

@syncable
async def async_run(
    file          : path,
    args          : list[str]   = [], 
    cwd           : path        = '.', 
    print_command : bool        = config.verbose,
    print_stdout  : bool        = config.verbose,
    print_stderr  : bool        = True,
    log_command   : path | None = None,
    log_stdout    : path | None = None,
    log_stderr    : path | None = None,
    return_stdout : bool        = False,
    return_stderr : bool        = False,
) -> None | str | tuple[str, str]:
    async with _internal_scheduler.schedule():
        if print_command:
            make_progress_logger.info(' '.join([file] + args))
        if log_command is not None:
            compile_commands_logger.log(file=log_command, command=[file] + args)
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
        if log_stdout is not None:
            with open(log_stdout, 'w') as logger:
                logger.write(stdout)
        if log_stderr is not None:
            with open(log_stderr, 'w') as logger:
                logger.write(stderr)
        exit_code = await proc.wait()
        if exit_code == 0:
            if not return_stdout and not return_stderr:
                return None
            elif not return_stdout and return_stderr:
                return stderr
            elif return_stdout and not return_stderr:
                return stdout
            else: # return_stdout and return_stderr
                return stdout, stderr
        else:
            raise SubprocessError(
                command        =[file] + args, 
                exit_code      =exit_code, 
                stdout         =stdout, 
                stderr         =stderr, 
                command_printed=not print_command, 
                stdout_printed =not print_stdout, 
                stderr_printed =not print_stderr
            )
