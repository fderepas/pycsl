r"""Test 5500 -- gen #37 route #383 allow-list addendum (expected FAIL): `d: Any` hashed by `{d}`, called with a list (CPython TypeError; PROVED at base b62ff2e23: a declared `Any` was checked only against the file's unhashable classes). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: an unknown class is not known hashable).
"""
# pycsl-expected: FAIL
from typing import Any

#@ no_exception \all
#@ ensures \result == 1
def g(d: Any) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g([1]))
