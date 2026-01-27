from cppmakelib.utility.time import time
import os
import shutil
import typing

path = str

def absolute_path     (path     : path)                -> path                 : ...
def copy_dir          (from_dir : path, to_dir : path) -> None                 : ...
def copy_file         (from_file: path, to_file: path) -> None                 : ...
def create_dir        (dir      : path)                -> None                 : ...
def create_file       (file     : path)                -> None                 : ...
def iterate_dir       (dir      : path)                -> typing.Iterable[path]: ...
def exist_dir         (dir      : path)                -> bool                 : ...
def exist_file        (file     : path)                -> bool                 : ...
def modified_time_file(file     : path)                -> time                 : ...
def parent_dir        (path     : path)                -> path                 : ...
def relative_path     (from_path: path, to_path: path) -> path                 : ...
def remove_dir        (dir      : path)                -> None                 : ...
def remove_file       (file     : path)                -> None                 : ...
def root_dir          (path     : path)                -> path                 : ...



def absolute_path(path: path) -> path:
    return os.path.abspath(path)

def copy_dir(from_dir: path, to_dir: path) -> None:
    shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)

def copy_file(from_file: path, to_file: path) -> None:
    shutil.copyfile(from_file, to_file)

def create_dir(dir: path) -> None:
    os.makedirs(dir, exist_ok=True)

def create_file(file: path) -> None:
    create_dir(parent_dir(file))
    open(file, 'w')

def iterate_dir(dir: path) -> typing.Iterable[path]:
    for root, _, filenames in os.walk(dir):
        for filename in filenames:
            yield f'{path(root)}/{filename}'

def exist_dir(dir: path) -> bool:
    return os.path.isdir(dir)

def exist_file(file: path) -> bool:
    return os.path.isfile(file)
        
def modified_time_file(file: path) -> time:
    return os.stat(file).st_mtime_ns

def parent_dir(self: path) -> path:
    return os.path.dirname(self)

def relative_path(from_path: path, to_path: path) -> path:
    return os.path.relpath(to_path, from_path)

def remove_dir(dir: path) -> None:
    shutil.rmtree(dir, ignore_errors=True)

def remove_file(file: path) -> None:
    try:
        os.remove(file)
    except FileNotFoundError:
        pass
        
def root_dir(path: path) -> path:
    return os.path.splitroot(path)[0]
