r"""Test 1330 — ROUTE #119 (carrier of the first #119 draft): `import multi_file_lib.r119_plainlib as plainlib; plainlib.inc = plainlib.dec` monkeypatches ANOTHER module, and `plainlib.inc(3)` PROVED `\result == 4` while CPython returns 2. The draft keyed on names defined in THIS file; an attribute write on an IMPORTED object is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

plainlib.inc = plainlib.dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
