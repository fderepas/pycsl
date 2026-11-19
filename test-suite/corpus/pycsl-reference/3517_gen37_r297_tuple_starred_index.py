r"""Test 3517 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. `t = (*ys, 5); t[1]` with ys = [7, 8]: CPython 8; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    ys: List[int] = [7, 8]
    t = (*ys, 5)
    return t[1]

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f() != 5, f()
