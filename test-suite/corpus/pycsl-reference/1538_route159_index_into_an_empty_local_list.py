r"""Test 1538 - ROUTE #159 (gen #29): `xs = []; return xs[0]` under `no_exception IndexError` - the bounds obligation used the placeholder's Why3 length 1024 and PROVED; CPython raises IndexError.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = []
    return xs[0]

