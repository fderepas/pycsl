r"""Test 6075 -- gen #37 route #416 (expected FAIL): `for k, v in d.items(): d[k + 100] = v` under `no_exception \all` (CPython RuntimeError; PROVED at base 4431ef86f). REFUSED (UB-7.1).
"""
# pycsl-expected: FAIL
from typing import Dict


#@ no_exception \all
def f(d: Dict[int, int]) -> int:
    for k, v in d.items():
        d[k + 100] = v
    return 0


if __name__ == "__main__":
    try:
        r = f({1: 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
