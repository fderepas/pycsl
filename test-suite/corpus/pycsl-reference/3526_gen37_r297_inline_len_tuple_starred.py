r"""Test 3526 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. INLINE `len((*ys, 5))`: CPython len(ys) + 1; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def f(ys: List[int]) -> int:
    return len((*ys, 5))

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f([]) != 2, f([])
