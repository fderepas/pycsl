r"""Test 3524 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. INLINE `len({1, 1})`: CPython 1 (route #54 fixed only the local); the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return len({1, 1})

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f() != 2, f()
