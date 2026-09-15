r"""Test 1350 — ROUTE #127: `pm = plainlib; pm.inc = abs` patches the imported module through an ALIAS; `plainlib.inc(-3)` PROVED `\result == -2` while CPython returns 3. A name bound to an object root is now an object root itself.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

pm = plainlib
pm.inc = abs


#@ ensures \result == -2
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(-3)
