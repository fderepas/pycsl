r"""Test 2345 — route #247 (expected FAIL): on an `Any` parameter the route #246 identity key compared
the parameter's tag with `tag_record` for BOTH classes, so `isinstance(x, pa)` and `isinstance(x, pb)`
were one term and `\result == 1` PROVED at afe28c69. CPython `f(pa(1))` = 0. The key now names the class.
"""
# pycsl-expected: FAIL
from typing import Any


class pa:
    def __init__(self, v: int) -> None:
        self.v = v


class pb:
    def __init__(self, v: int) -> None:
        self.v = v


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    a = 0
    if isinstance(x, pa):
        a = 1
    b = 0
    if isinstance(x, pb):
        b = 1
    if a == 1 and b == 0:
        return 0
    return 1


if __name__ == "__main__":
    assert f(pa(1)) == 0
