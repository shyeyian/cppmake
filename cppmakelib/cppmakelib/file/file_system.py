from cppmakelib.basic.config  import config
from cppmakelib.utility.color import yellow
import os
import shutil

def absolute_path (path):        ...
def relative_path (path, from_): ...
def parent_path   (path):        ...
def canonical_path(path):        ...
def base_path     (path):        ...
def exist_file    (file):        ...
def exist_dir     (dir):         ...
def create_file   (file):        ...
def create_dir    (dir):         ...
def copy_file     (file, to):    ...
def copy_dir      (dir,  to):    ...
def remove_file   (file):        ...
def remove_dir    (dir):         ...



def absolute_path(path):
    return os.path.abspath(path)

def relative_path(path, from_):
    return os.path.relpath(path, from_)

def parent_path(path):
    return os.path.dirname(path)

def canonical_path(path):
    return os.path.relpath(path, '.')

def base_path(path):
    return os.path.basename(path)

def exist_file(file):
    return os.path.isfile(file)

def exist_dir(dir):
    return os.path.isdir(dir)

def create_file(file):
    if config.verbose and not exist_file(file):
        print(yellow(f"touch {file}"))
    open(file, 'w')

def create_dir(dir):
    if config.verbose and not exist_dir(dir):
        print(yellow(f"mkdir -p {dir}"))
    os.makedirs(dir, exist_ok=True)

def copy_file(file, to):
    if config.verbose:
        print(yellow(f"cp {file} {to}"))
    create_dir(parent_path(to))
    shutil.copyfile(file, to)

def copy_dir(dir, to):
    if config.verbose:
        print(yellow(f"cp -r {dir} {to}"))
    create_dir(parent_path(to))
    shutil.copytree(dir, to, dirs_exist_ok=True)

def remove_file(file):
    if config.verbose and exist_file(file):
        print(yellow(f"rm {file}"))
    os.remove(file)

def remove_dir(dir):
    if config.verbose and exist_dir(dir):
        print(yellow(f"rm -r {dir}"))
    shutil.rmtree(dir)

def modified_time_of_file(file):
    return os.path.getmtime(file)

def modified_time_of_dir(dir):
    return os.path.getmtime(dir)

def iterate_dir(dir, recursive):
    if not recursive:
        return [f"{dir}/{file}" for file in os.listdir(dir) if exist_file(f"{dir}/{file}")]
    else:
        return [f"{root}/{file}" for root, _, files in os.walk(dir) for file in files]