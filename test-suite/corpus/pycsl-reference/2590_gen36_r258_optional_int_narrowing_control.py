r"""Test 2590 — route #258 (expected PASS): CONTROL: an `Optional[int]` parameter keeps its two-armed
variant (no arm is erased), so `x is not None` still narrows to the `int` payload and
`x + 1 - x == 1` is decided.
"""
# pycsl-expected: PASS
from typing import Optional


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Optional[int]) -> int:
    if x is not None:
        return x + 1 - x
    return 1


if __name__ == "__main__":
    assert f(3) == 1 and f(None) == 1
