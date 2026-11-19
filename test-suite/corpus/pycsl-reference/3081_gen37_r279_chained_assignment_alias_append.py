r"""Test 3081 — route #279 (expected FAIL): `a = b = []` binds ONE list to two names; the desugaring
(`_pycsl_multi_1 = []; a = _pycsl_multi_1; b = _pycsl_multi_1`) lowered both to copies, so after
`b.append(1)` the claim `len(a) == 0` PROVED at 72ab1c57 (red-team p216). CPython: 1. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = []
    b: List[int] = []
    a = b = []
    b.append(1)
    return len(a)


if __name__ == "__main__":
    assert f() == 1
