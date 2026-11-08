r"""Test 1405 — ROUTE #138: the same arm also keyed on the SYNTACTIC SHAPE `Call(func=Call(getattr, ...))`. `sa = getattr(builtins, "set" + "attr"); sa(plainlib, "inc", plainlib.dec)` binds the result first, so the shape never appears; it PROVED `plainlib.inc(3) == 4` while CPython returns 2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib
import builtins

sa = getattr(builtins, "set" + "attr")
sa(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)