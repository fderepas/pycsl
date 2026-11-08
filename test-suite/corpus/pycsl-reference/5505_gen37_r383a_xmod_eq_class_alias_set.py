r"""Test 5505 -- gen #37 route #383 allow-list addendum (expected FAIL): `from multi_file_lib.r383a_eqlib import D as E; D = E`, `{d}` (CPython TypeError; PROVED at base b62ff2e23). REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
from multi_file_lib.r383a_eqlib import D as E
D = E

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
