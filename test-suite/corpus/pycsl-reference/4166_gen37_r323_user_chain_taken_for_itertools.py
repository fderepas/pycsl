r"""Test 4166 -- gen #37 route #323 (expected FAIL): A user `def chain(..): return [0]` was modelled as itertools' (`== 4` PROVED, CPython 1). FAILS.
"""
# pycsl-expected: FAIL
from typing import List

#@ assigns \nothing
def chain(a: List[int], b: List[int]) -> List[int]:
    return [0]

#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return len(list(chain([1, 2], [3, 4])))

if __name__ == "__main__":
    assert f() == 4, f()
