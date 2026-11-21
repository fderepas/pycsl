r"""Test 4174 -- gen #37 route #323 (expected PASS): CONTROL: `import itertools as it` / `from itertools import chain as ch` resolve to itertools: `len(list(it.product(a, b))) + len(list(ch(a, b))) == 11` PROVES.
"""
# pycsl-expected: PASS
import itertools as it
from itertools import chain as ch
from typing import List
#@ requires len(a) == 2
#@ requires len(b) == 3
#@ ensures \result == 11
#@ assigns \nothing
def f(a: List[int], b: List[int]) -> int:
    return len(list(it.product(a, b))) + len(list(ch(a, b)))

if __name__ == "__main__":
    assert f([1, 2], [3, 4, 5]) == 11, f([1, 2], [3, 4, 5])
