r"""Test 3516 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. 3515 read through a local `r = d[0]; return r + 0`; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
def f(k: int) -> int:
    d: Dict[int, int] = {0: 1, k: 2}
    r = d[0]
    return r + 0

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f(0) != 1, f(0)
