r"""Test 1539 - ROUTE #159 (gen #29): `[][0]` lowered to the erased `subscript_get 0 0` with NO IndexError obligation and PROVED `no_exception IndexError`; CPython raises. An erased read now carries an unprovable (length 0) obligation.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    return [][0]

