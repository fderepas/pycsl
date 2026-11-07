r"""Test 5074 -- gen #37 route #375 (expected FAIL): NEW shape: `t = 0; t += x` with `x: Any` under `no_exception \all` (CPython TypeError for a str). FAILS now (PyCSL-R375).
"""
# pycsl-expected: FAIL
from typing import Any

#@ no_exception \all
def f(x: Any) -> int:
    t = 0
    t += x
    return 0

if __name__ == "__main__":
    print(f("a"))
