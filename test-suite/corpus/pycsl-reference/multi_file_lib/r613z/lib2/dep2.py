# u60 control 10332: `from .r613z_one import one` is package-relative in CPython and in pycsl alike, so
# the program directory's r613z_one.py plays no part.
from .r613z_one import one


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return one()
