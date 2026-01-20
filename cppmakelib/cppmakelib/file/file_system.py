from cppmakelib.utility.decorator import member
from cppmakelib.utility.time      import Time
import pathlib
import shutil
import typing

class Path:
    def __init__     (self, filesystem_str: str = '')   -> None: ...
    def absolute_path(self)                             -> Path: ...
    def relative_path(self, from_path: Path)            -> Path: ...
    def parent_path  (self)                             -> Path: ...
    def root_path    (self)                             -> Path: ...
    def __str__      (self)                             -> str : ...
    def __truediv__  (self, filesystem_str: str | Path) -> Path: ...
    def __rtruediv__ (self, filesystem_str: str | Path) -> Path: ...
    
    _handle: pathlib.Path
    @staticmethod
    def _from_handle(handle: pathlib.Path) -> Path: ...

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
def __init__(self: Path, filesystem_str: str = '') -> None:
    self._handle = pathlib.Path(filesystem_str)

@member(Path)
def absolute(self: Path) -> Path:
    return Path._from_handle(self._handle.absolute())

@member(Path)
def relative(self: Path, from_: Path) -> Path:
    return Path._from_handle(self._handle.relative_to(from_._handle))

@member(Path)
def parent(self: Path, from_: Path) -> Path:
    return Path._from_handle(self._handle.parent)

@member(Path)
def root_path(self: Path) -> Path:
    return Path(self._handle.root)

@member(Path)
def __str__(self: Path) -> str:
    return self._handle.__str__()

@member(Path)
def __truediv__(self: Path, filesystem_str: str | Path) -> Path:
    if isinstance(filesystem_str, str):
        return Path._from_handle(self._handle / filesystem_str)
    else: # isinstance(filesystem_str, Path)
        return Path._from_handle(self._handle / filesystem_str._handle)
    
@member(Path)
def __rtruediv__(self: Path, filesystem_str: str | Path) -> Path:
    if isinstance(filesystem_str, str):
        return Path._from_handle(filesystem_str / self._handle)
    else: # isinstance(filesystem_str, Path)
        return Path._from_handle(filesystem_str._handle / self._handle)
    
@member(Path)
@staticmethod
def _from_handle(handle: pathlib.Path) -> Path:
    path = Path()
    path._handle = handle
    return path

def exist_file(file: Path) -> bool:
    return file._handle.is_file()

def exist_dir(dir: Path) -> bool:
    return dir._handle.is_dir()

def create_file(file: Path) -> None:
    create_dir(file.parent_path())
    file._handle.touch(exist_ok=True)

def create_dir(dir: Path) -> None:
    dir._handle.mkdir(parents=True, exist_ok=True)

def copy_file(from_file: Path, to_file: Path) -> None:
    from_file._handle.copy(to_file._handle)

def copy_dir(from_dir: Path, to_dir: Path) -> None:
    from_dir._handle.copy(to_dir._handle)

def remove_file(file: Path) -> None:
    file._handle.unlink(missing_ok=True)

def remove_dir(dir: Path) -> None:
    shutil.rmtree(dir._handle, ignore_errors=True)

def mtime_file(file: Path) -> Time:
    return file._handle.stat().st_mtime

def iterate_dir(dir: Path) -> typing.Iterable[Path]:
    for _subhandle in dir._handle.rglob('*'):
        if _subhandle.is_file():
            yield Path._from_handle(_subhandle)

    
