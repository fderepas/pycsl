r"""Test 1396 — ROUTE #136: the namespace builtin reached by a COMPUTED `getattr` that is then CALLED — `getattr(builtins, "set" + "attr")(plainlib, "inc", plainlib.dec)` — names none of the guarded spellings. It PROVED `plainlib.inc(3) == 4` while CPython returns 2. #127 already refuses a computed `getattr` on the WRITE side; this is its read side (census of `getattr(...)(...)`: 0 sites).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import builtins
import multi_file_lib.r119_plainlib as plainlib

getattr(builtins, "set" + "attr")(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
