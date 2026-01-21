from cppmakelib.utility.decorator import member
from cppmakelib.utility.time      import Time
import os
import shutil
import typing

class Path(str):
    def __new__      (cls,  path: str)       -> Path: ...
    def __truediv__  (self, path: str)       -> Path: ...
    def __rtruediv__ (self, path: str)       -> Path: ...
    def absolute_path(self)                  -> Path: ...
    def relative_path(self, from_path: Path) -> Path: ...
    def parent_path  (self)                  -> Path: ...
    def root_path    (self)                  -> Path: ...

class UnresolvedPath(str):
    def resolved_path(self) -> Path: ...

def exist_file (file     : Path)                -> bool                 : ...
def exist_dir  (dir      : Path)                -> bool                 : ...
def create_file(file     : Path)                -> None                 : ...
def create_dir (dir      : Path)                -> None                 : ...
def copy_file  (from_file: Path, to_file: Path) -> None                 : ...
def copy_dir   (from_dir : Path, to_dir : Path) -> None                 : ...
def remove_file(file     : Path)                -> None                 : ...
def remove_dir (dir      : Path)                -> None                 : ...
def mtime_file (file     : Path)                -> Time                 : ...
def iterate_dir(dir      : Path)                -> typing.Iterable[Path]: ...



@member(Path)
def __new__(cls: type[Path], path: str) -> Path:
    return super(cls, cls).__new__(cls, path)

@member(Path)
def __truediv__(self: Path, path: str) -> Path:
    return Path(os.path.join(self, path))
    
@member(Path)
def __rtruediv__(self: Path, path: str) -> Path:
    return Path(os.path.join(path, self))

@member(Path)
def absolute_path(self: Path) -> Path:
    return Path(os.path.abspath(self))

@member(Path)
def relative_path(self: Path, from_: Path) -> Path:
    return Path(os.path.relpath(self, from_))

@member(Path)
def parent_path(self: Path) -> Path:
    return Path(os.path.dirname(self))

@member(Path)
def root_path(self: Path) -> Path:
    return Path(os.path.splitroot(self)[0])

@member(UnresolvedPath)
def resolved_path(self: UnresolvedPath) -> Path:
    resolved = shutil.which(self)
    if resolved is None:
        raise FileNotFoundError(self)
    return Path(resolved)

def exist_file(file: Path) -> bool:
    return os.path.isfile(file)

def exist_dir(dir: Path) -> bool:
    return os.path.isdir(dir)

def create_file(file: Path) -> None:
    create_dir(file.parent_path())
    open(file, 'w')

def create_dir(dir: Path) -> None:
    os.makedirs(dir, exist_ok=True)

def copy_file(from_file: Path, to_file: Path) -> None:
    shutil.copyfile(from_file, to_file)

def copy_dir(from_dir: Path, to_dir: Path) -> None:
    shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)

def remove_file(file: Path) -> None:
    try:
        os.remove(file)
    except FileNotFoundError:
        pass

def remove_dir(dir: Path) -> None:
    shutil.rmtree(dir, ignore_errors=True)

def mtime_file(file: Path) -> Time:
    return Time(os.stat(file).st_mtime)

def iterate_dir(dir: Path) -> typing.Iterable[Path]:
    for root, _, filenames in os.walk(dir):
        for filename in filenames:
            yield Path(root)/filename

