r"""Test 4169 -- gen #37 route #323 (expected FAIL): A user `def list(a): return [0]` was taken for the builtin by the length model. FAILS.
"""
# pycsl-expected: FAIL
from typing import List
#@ assigns \nothing
def list(a: List[int]) -> List[int]:
    return [0]

#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return len(list([1, 2, 3]))

if __name__ == "__main__":
    assert f() == 3, f()
