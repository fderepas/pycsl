r"""Test 1381 — ROUTE #135 (star arm, order 2): `from ...r135_aliaslib import *` exports `pm`, an alias of plainlib, and `pm.inc = plainlib.dec` at module scope patched it; an unbound receiver name was exempt, and `plainlib.inc(3)` PROVED `\result == 4` while CPython returns 2. An unbound receiver is now exempt only in a file without a star import.
"""
# pycsl-expected: FAIL
from multi_file_lib.r135_aliaslib import *
import multi_file_lib.r119_plainlib as plainlib

pm.inc = plainlib.dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
