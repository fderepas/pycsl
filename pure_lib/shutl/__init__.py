# pure_lib/shutl — pure-Python shutil module
# Over fs (compositions of os primitives). Modelled.


class SameFileError(Exception):
    pass


class SpecialFileError(Exception):
    pass


#@ ensures \result >= 0
def copyfileobj(fsrc, fdst, length) -> int:
    return 0


#@ ensures \result >= 0
def copyfile(src, dst) -> int:
    return 0


#@ ensures \result >= 0
def copystat(src, dst) -> int:
    return 0


#@ ensures \result >= 0
def copy2(src, dst) -> int:
    return 0


#@ ensures \result >= 0
def rmtree(path) -> int:
    return 0


#@ ensures \result >= 0
def which(name) -> int:
    return 0
