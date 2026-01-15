from cppmakelib.basic.config            import config
from cppmakelib.error.subprocess        import SubprocessError
from cppmakelib.execution.scheduler     import Scheduler
from cppmakelib.logger.compile_commands import compile_commands_logger
from cppmakelib.utility.color           import yellow
from cppmakelib.utility.decorator       import syncable
import asyncio
import sys
import time

def             run(*args, **kwargs): ...
async def async_run(*args, **kwargs): ...



_internal_scheduler = Scheduler(config.parallel)

@syncable
async def async_run(
    command,
    cwd           ='.', 
    print_command =config.verbose,
    log_command   =(False, None), # (True, file)
    run_command   =True,
    input_stdin   =None,
    print_stdout  =config.verbose,
    return_stdout =False,
    print_stderr  =True,
    log_stderr    =(False, None), # (True, callback)
    return_stderr =False,
    timeout       =None
):
    async with _internal_scheduler.schedule():
        if print_command:
            print(yellow(' '.join(command)))
        if log_command[0] == True:
            compile_commands_logger.log_command(command=command, file=log_command[1])
        if run_command:
            proc = await asyncio.subprocess.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdin =asyncio.subprocess.PIPE if input_stdin is not None else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            try:
                async def write_stream(stream, from_):
                    if from_ is not None:
                        stream.write(from_.encode())
                        await stream.drain()
                        stream.close()
                async def read_stream(stream, to, tee):
                    while True:
                        line = await stream.readline()
                        if not stream.at_eof():
                            line = line.decode()
                            to += [line]
                        else:
                            break
                        if tee is not None:
                            print(line, end='', file=tee)
                stdin  = input_stdin
                stdout = []
                stderr = []
                deadline = time.time() + timeout if timeout is not None else None
                await asyncio.wait_for(
                    asyncio.gather(
                        write_stream(stream=proc.stdin,  from_=stdin),
                        read_stream (stream=proc.stdout, to=stdout, tee=sys.stdout if print_stdout else None), 
                        read_stream (stream=proc.stderr, to=stderr, tee=sys.stderr if print_stderr else None)
                    ),
                    timeout=deadline-time.time() if deadline is not None else None
                )
                code = await asyncio.wait_for(
                    proc.wait(),
                    timeout=deadline-time.time() if deadline is not None else None
                )
                stdout = ''.join(stdout)
                stderr = ''.join(stderr)
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                raise TimeoutError(f'process {' '.join(command)} timeouts after {timeout} seconds')
            if log_stderr[0] == True:
                log_stderr[1](stderr) 
            if code == 0:
                return (stdout, stderr) if return_stdout and return_stderr else \
                        stdout          if return_stdout                   else \
                                stderr  if                   return_stderr else \
                        None
            else:
                raise SubprocessError(stderr=stderr, is_stderr_printed=print_stderr, code=code)
