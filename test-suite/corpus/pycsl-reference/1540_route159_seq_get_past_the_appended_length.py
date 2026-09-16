r"""Test 1540 - ROUTE #159 (gen #29): `xs = []; xs.append(1); return xs[3]` - `Seq.get` is total in Why3 and the read carried no IndexError obligation; PROVED, CPython raises.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = []
    xs.append(1)
    return xs[3]

