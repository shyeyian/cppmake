from cppmakelib.unit.binary import Binary

class Dynamic(Binary):
    def __new__  (cls,  file: path) -> Dynamic: ...
    def __init__ (self, file: path) -> None   : ...



from cppmakelib.utility.decorator  import member, unique
from cppmakelib.utility.filesystem import path

@member(Dynamic)
@unique
def __init__(self: Dynamic, file: path) -> None:
    super(Dynamic, self).__init__(file)
    