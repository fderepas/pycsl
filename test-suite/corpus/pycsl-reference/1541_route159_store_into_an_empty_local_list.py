r"""Test 1541 - ROUTE #159 (gen #29): `xs = []; xs[0] = 5` under `no_exception IndexError` bounded the store by 1024 and PROVED; CPython raises.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = []
    xs[0] = 5
    return 1

