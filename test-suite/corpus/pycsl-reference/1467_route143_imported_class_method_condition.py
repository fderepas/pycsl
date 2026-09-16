r"""Test 1467 - ROUTE #143 through an IMPORTED CLASS: `K.m`'s `raises ValueError when LIM < 0` was folded against the importer's `LIM = 5`; PROVED at HEAD, CPython raises. Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r143_cls import K

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    o = K(1)
    return o.m(k)

