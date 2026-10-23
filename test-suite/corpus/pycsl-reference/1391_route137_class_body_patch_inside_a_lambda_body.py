r"""Test 1391 — ROUTE #137: the CLASS-BODY spelling of test 1389 — a class body is executed exactly like module scope, and the lambda hid the patch from the sink walk there too. PROVED `plainlib.inc(3) == 4`; CPython returns 2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib


class K:
    _j = (lambda m: setattr(m, "inc", plainlib.dec))(plainlib)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
