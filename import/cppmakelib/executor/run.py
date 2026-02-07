from cppmakelib.basic.config import config
import typing

@typing.overload
async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[False] = False) -> None           : ...
@typing.overload
async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[False] = False, return_stderr: typing.Literal[True])          -> str            : ...
@typing.overload
async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[False] = False) -> str            : ...
@typing.overload
async def async_run(file: path, args: list[str] = [], cwd: path = '.', print_command: bool = config.verbose, print_stdout: bool = config.verbose, print_stderr: bool = True, log_command: path | None = None, log_stdout: path | None = None, log_stderr: path | None = None, *, return_stdout: typing.Literal[True],          return_stderr: typing.Literal[True])          -> tuple[str, str]: ...



from cppmakelib.error.subprocess        import SubprocessError
from cppmakelib.executor.operation      import when_all
from cppmakelib.executor.scheduler      import Scheduler
from cppmakelib.logger.compile_commands import compile_commands_logger
from cppmakelib.utility.filesystem      import path
import asyncio
import sys

_internal_scheduler = Scheduler(config.jobs)
async def async_run(
    file         : path,
    args         : list[str]   = [], 
    cwd          : path        = '.', 
    print_command: bool        = config.verbose,
    print_stdout : bool        = config.verbose,
    print_stderr : bool        = True,
    log_command  : path | None = None,
    log_stdout   : path | None = None,
    log_stderr   : path | None = None,
    return_stdout: bool        = False,
    return_stderr: bool        = False,
) -> None | str | tuple[str, str]:
    global _internal_scheduler
    async with _internal_scheduler.schedule():
        if print_command:
            print(' '.join([file] + args))
        if log_command is not None:
            compile_commands_logger.log(file=log_command, command=[file] + args)
        proc = await asyncio.subprocess.create_subprocess_exec(
            file, 
            *args,
            cwd   =cwd,
            stdin =asyncio.subprocess.DEVNULL,
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
            open(log_stdout, 'w').write(stdout)
        if log_stderr is not None:
            open(log_stderr, 'w').write(stderr)
        exit_code = await proc.wait()
        if exit_code == 0:
            if not return_stdout and not return_stderr:
                return None
            elif not return_stdout and return_stderr:
                return stderr
            elif return_stdout and not return_stderr:
                return stdout
            elif return_stdout and return_stderr:
                return stdout, stderr
            else:
                assert False
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
