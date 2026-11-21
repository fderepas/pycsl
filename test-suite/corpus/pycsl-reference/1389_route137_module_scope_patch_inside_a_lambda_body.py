r"""Test 1389 — ROUTE #137: route #135's sink walk `continue`d on every `Lambda`, and #119 rule (6) exempts a PARAMETER receiver, so `(lambda m: setattr(m, "inc", plainlib.dec))(plainlib)` at module scope passed both fences; `plainlib.inc(3)` PROVED `\result == 4` while CPython runs `dec` and returns 2. A lambda body is now part of the module-executed region, and a lambda parameter is never a "fresh" receiver.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

(lambda m: setattr(m, "inc", plainlib.dec))(plainlib)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
