from cppmake.basic.config import config
import os
import shutil

def absolute_path (path):        ...
def relative_path (path, from_): ...
def parent_path   (path):        ...
def canonical_path(path):        ...
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
    return relative_path(path, from_='.')

def exist_file(file):
    return os.path.isfile(file)

def exist_dir(dir):
    return os.path.isdir(dir)

def create_file(file):
    if not exist_file(file) and config.verbose:
        print(f">>> touch {file}")
    try:
        open(file, 'w')
    except:
        pass

def create_dir(dir):
    if not exist_dir(dir) and config.verbose:
        print(f">>> mkdir -p {dir}")
    try:
        os.makedirs(dir, exist_ok=True)
    except:
        pass

def copy_file(file, to):
    if config.verbose:
        print(f">>> cp {file} {to}")
    create_dir(parent_path(to))
    try:
        shutil.copyfile(file, to)
    except:
        pass

def copy_dir(dir, to):
    if config.verbose:
        print(f">>> cp -r {dir} {to}")
    create_dir(parent_path(to))
    try:
        shutil.copytree(dir, to, dirs_exist_ok=True)
    except:
        pass

def remove_file(file):
    if exist_file(file) and config.verbose:
        print(f">>> rm {file}")
    try:
        os.remove(file)
    except:
        pass

def remove_dir(dir):
    if exist_dir(dir) and config.verbose:
        print(f">>> rm -r {dir}")
    try:
        shutil.rmtree(dir)
    except:
        pass

def modified_time_of_file(file):
    return os.path.getmtime(file)

def iterate_dir(dir, recursive):
    if not recursive:
        return [f"{dir}/{file}" for file in os.listdir(dir) if exist_file(f"{dir}/{file}")]
    else:
        return [f"{root}/{file}" for root, _, files in os.walk(dir) for file in files]