r"""Test 3512 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. `{1: 1, +1: 2}[1]`: CPython 2; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1, +1: 2}
    return d[1]

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f() != 1, f()
