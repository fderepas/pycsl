r"""Test 1543 - ROUTE #159 (gen #29): `(1, 2)[5]` lowered to the erased `subscript_get` and PROVED `no_exception IndexError`; CPython raises.
"""
# pycsl-expected: FAIL
from typing import Tuple
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    t = (1, 2)
    return t[5]

