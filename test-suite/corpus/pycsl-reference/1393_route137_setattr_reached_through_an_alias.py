r"""Test 1393 — ROUTE #137: every namespace guard (#118, #119, #127 and route #135's sink) keys on the SPELLING `setattr`. One alias defeats them all: `sa = setattr; sa(plainlib, "inc", plainlib.dec)` PROVED `plainlib.inc(3) == 4` while CPython returns 2. A namespace-reaching builtin READ as a value is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

sa = setattr
sa(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
