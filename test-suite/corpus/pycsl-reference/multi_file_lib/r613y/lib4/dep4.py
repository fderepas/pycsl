# u61 witness 10344 (control): a dotted PACKAGE-RELATIVE import whose every prefix is a regular package in
# this one directory; CPython and pycsl read the same files.
from .zpq61.b import one


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return one()
