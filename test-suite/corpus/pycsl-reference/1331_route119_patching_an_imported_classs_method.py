r"""Test 1331 — ROUTE #119: `from multi_file_lib.r119_plainlib import K; K.m = K.n` patches an IMPORTED class, and `K().m()` PROVED `\result == 1` while CPython returns 2. Refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_plainlib import K

K.m = K.n


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    k = K()
    return k.m()
