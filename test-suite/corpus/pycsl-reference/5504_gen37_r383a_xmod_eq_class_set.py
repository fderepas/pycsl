r"""Test 5504 -- gen #37 route #383 allow-list addendum (expected FAIL): `from multi_file_lib.r383a_eqlib import D` (a plain class with `__eq__` and no `__hash__`, no stdlib base: S1 does not apply), `{d}` (CPython TypeError; PROVED at base b62ff2e23). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: a class of a non-stdlib module is an unknown class).
"""
# pycsl-expected: FAIL
from multi_file_lib.r383a_eqlib import D

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
