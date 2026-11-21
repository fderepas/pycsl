r"""Test 2444 — route #251 (expected FAIL): `return x % 1` on `x: Any` PROVED `\result == 0` (integer `mod`). CPython:
`f(0.5)` is `0.5` — no user class needed.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return x % 1


if __name__ == "__main__":
    assert f(0.5) == 0.5
