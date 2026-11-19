r"""Test 3520 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. `len((*ys, 5))` local with ys = [7, 8]: CPython 3; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    ys: List[int] = [7, 8]
    t = (*ys, 5)
    return len(t)

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f() != 2, f()
