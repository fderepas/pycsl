r"""Test 3525 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. INLINE `len({0: 1, k: 2})` with k == 0: CPython 1; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def f(k: int) -> int:
    return len({0: 1, k: 2})

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f(0) != 2, f(0)
