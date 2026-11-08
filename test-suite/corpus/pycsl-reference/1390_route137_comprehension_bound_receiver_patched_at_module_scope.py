r"""Test 1390 — ROUTE #137: route #135's `_nb_fresh_ok` was built only from Assign/AnnAssign/NamedExpr/For/withitem targets, so a COMPREHENSION-bound name fell to the "no module-scope binding" default and counted as FRESH. `[setattr(m, "inc", plainlib.dec) for m in [plainlib]]` PROVED `plainlib.inc(3) == 4` while CPython returns 2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

_junk = [setattr(m, "inc", plainlib.dec) for m in [plainlib]]


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
