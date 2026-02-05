from cppmakelib.system.all         import system
from cppmakelib.utility.decorator  import member
from cppmakelib.utility.filesystem import path
import argparse
import os
import typing

class Config(argparse.Namespace):
    def __init__    (self)                            -> None: ...
    def add_argument(self, *args: ..., **kwargs: ...) -> None: ... # TODO: add typing support, which forwards 'argparse.ArgumentParser.add_argument'. Notice 'functools.wraps' fails on 'self'.
    project : path
    target  : str
    compiler: path
    std     : typing.Literal['c++20'] | typing.Literal['c++23']   | typing.Literal['c++26']
    type    : typing.Literal['debug'] | typing.Literal['release'] | typing.Literal['size']
    jobs    : int
    verbose : bool

    _parser : argparse.ArgumentParser

config: Config



@member(Config)
def __init__(self: Config) -> None:
    self._parser = argparse.ArgumentParser()
    self._parser.usage = 'cppmake [project] [options...]'
    self._parser.add_argument('project',    nargs='?',                            default='.',                  help=f'path to C++ project dir   (example: ., .., /home/my/project; requires: containing cppmake.py; default: .)')
    self._parser.add_argument('--target',                                         default='make',               help=f'select cppmake target     (example: make, build, test; requires: defined in cppmake.py; default: make)')
    self._parser.add_argument('--compiler',                                       default=system.compiler,      help=f'use specific C++ compiler (example: g++, /usr/bin/g++, /opt/homebrew/clang++; requires: executable; default: {system.compiler})')
    self._parser.add_argument('--std',      choices=['c++20', 'c++23', 'c++26'],  default='c++26',              help=f'use specific C++ standard (default: c++26)')
    self._parser.add_argument('--type',     choices=['debug', 'release', 'size'], default='debug',              help=f'choose config type        (default: debug)')
    self._parser.add_argument('--jobs',     type   =lambda n: int(n),             default=os.cpu_count(),       help=f'allow maximun concurrency (default: {os.cpu_count()})')
    self._parser.add_argument('--verbose',  action ='store_true',                 default=False,                help=f'print verbose outputs')
    self._parser.parse_args(namespace=self)

@member(Config)
def add_argument(self: Config, *args: ..., **kwargs: ...) -> None:
    self._parser.add_argument(*args, **kwargs)
    self._parser.parse_args(namespace=self)

config = Config()

os.chdir(config.project)
os.environ['LANG'] = 'C'
