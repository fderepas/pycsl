r"""Test 1546 - ROUTE #159 (gen #29): `{}[1]` lowered to the erased `subscript_get 0 1` with no KeyError obligation and PROVED `no_exception KeyError`; CPython raises KeyError.
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ no_exception KeyError
def probe() -> int:
    return {}[1]

