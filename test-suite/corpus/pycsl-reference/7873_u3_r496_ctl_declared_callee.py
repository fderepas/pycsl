r"""Test 7873 -- route #496 (control, expected PASS): g holds `chr(n)` but DECLARES `#@ no_exception ValueError` under `requires 0 <= n < 256`, so the call is checked in g; f catches ValueError; CPython f(65) returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

#@ requires 0 <= n and n < 256
#@ ensures \result == 1
#@ no_exception ValueError
def g(n: int) -> int:
    y = chr(n)
    return 1


#@ requires 0 <= n and n < 256
#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 2


if __name__ == "__main__":
    assert f(65) == 1 and f(0) == 1
