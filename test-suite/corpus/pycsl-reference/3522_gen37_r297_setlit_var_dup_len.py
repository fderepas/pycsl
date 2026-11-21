r"""Test 3522 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. `requires a == b`, `len({a, b})`: CPython 1; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ requires a == b
#@ ensures \result == 2
#@ assigns \nothing
def f(a: int, b: int) -> int:
    s = {a, b}
    return len(s)

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f(1, 1) != 2, f(1, 1)
