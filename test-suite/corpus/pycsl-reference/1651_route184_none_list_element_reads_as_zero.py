r"""Test 1651 - ROUTE #184 (gen #29): `xs: List[Optional[int]] = [None]` lowered to `Array.make 1 0`, so `xs[0] == 0` PROVED True (CPython False) - route #56's shape on a LIST ELEMENT. A `None` element now lowers to route #44's opaque `pycsl_none`.
"""
# pycsl-expected: FAIL
from typing import List, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    xs: List[Optional[int]] = [None]
    return xs[0] == 0
