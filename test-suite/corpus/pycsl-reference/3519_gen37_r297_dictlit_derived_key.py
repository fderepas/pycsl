r"""Test 3519 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. `i = n - 1; {0: 1, i: 2}[0]` with n == 1: CPython 2; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ requires n >= 1
#@ ensures \result == 1
#@ assigns \nothing
def f(n: int) -> int:
    i = n - 1
    d: Dict[int, int] = {0: 1, i: 2}
    return d[0]

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f(1) != 1, f(1)
