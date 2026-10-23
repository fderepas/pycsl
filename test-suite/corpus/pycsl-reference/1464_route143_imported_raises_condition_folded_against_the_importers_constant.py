r"""Test 1464 - ROUTE #143 (found gen #27, closed gen #29): `f`'s `raises ValueError when LIM < 0` names ITS module's `LIM = -1`, and the importer binds its own `LIM = 5`. The injected `val` carried `raises { ValueError -> ((5) < 0) }` and `no_exception ValueError` PROVED while CPython raises. Now REFUSED: a name free in an imported contract that the importer rebinds.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)
