r"""Test 3917 -- gen #37 route #307 (expected PASS): CONTROL: pure operands and ordinary arithmetic (no effectful operand): emission unchanged, proves.
"""
# pycsl-expected: PASS
from typing import List

#@ assigns \nothing
#@ ensures \result == a - b
def sub(a: int, b: int) -> int:
    return a - b

#@ requires len(a) >= 1 and len(b) >= 1
#@ ensures \result == len(a) * 2 - len(b) + a[0] - (a[0] - b[0]) - b[0] + 1
def f(a: List[int], b: List[int]) -> int:
    x = len(a) + len(a)
    y = sub(a[0], b[0])
    return x - len(b) + a[0] - y - b[0] + 1

if __name__ == "__main__":
    assert f([1], [2, 3]) == 1
