r"""Test 4165 -- gen #37 route #323 (expected FAIL): A user `def product(a, b): return [0]` was modelled as itertools' and `len(list(product([1, 2], [3, 4]))) == 4` PROVED (CPython 1). The callee must resolve to itertools: FAILS.
"""
# pycsl-expected: FAIL
from typing import List


#@ assigns \nothing
def product(a: List[int], b: List[int]) -> List[int]:
    return [0]

#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return len(list(product([1, 2], [3, 4])))

if __name__ == "__main__":
    assert f() == 4, f()
