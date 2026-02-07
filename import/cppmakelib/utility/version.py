import functools

@functools.total_ordering
class Version:
    class ParseError(Exception):
        pattern : str
        string  : str
        position: int
    def __init__(self, subversions: list[int])                        -> None   : ...
    def __str__ (self)                                                -> str    : ...
    def __eq__  (self, other_version: Version | object)               -> bool   : ...
    def __lt__  (self, other_version: Version | int | float | object) -> bool   : ...
    @staticmethod
    def parse   (pattern: str, string: str)                           -> Version: ...
    subversions: list[int]



from cppmakelib.utility.decorator import member
import re

@member(Version)
def __init__(self: Version, subversions: list[int]) -> None:
    self.subversions = subversions

@member(Version)
def __str__(self: Version) -> str:
    return '.'.join([str(subversion) for subversion in self.subversions])

@member(Version)
def __eq__(self: Version, other: Version | object) -> bool:
    if isinstance(other, Version):
        return self.subversions == other.subversions
    else:
        return NotImplemented
    
@member(Version)
def __lt__(self: Version, other: Version | int | float | object) -> bool:
    if isinstance(other, Version):
        return self.subversions < other.subversions
    elif isinstance(other, int):
        return self.subversions[0] < other
    elif isinstance(other, float):
        return self.subversions[0] <  int(other) or \
               self.subversions[0] == int(other) and self.subversions[1] < int(str(other).partition('.')[2])
    else:
        return NotImplemented
    
@member(Version)
def parse(pattern: str, string: str):
    versions = re.findall(pattern=pattern, string=string)
    if len(versions) == 0:
        raise Version.ParseError(f'failed to parse version (with pattern = {pattern}, string = {string})')
    elif len(versions) == 1:
        return Version([int(subversion) for subversion in versions[0]])
    elif len(versions) >= 2:
        raise Version.ParseError(f'ambiguous version (with pattern = {pattern}, string = {string})')
    else:
        assert False
