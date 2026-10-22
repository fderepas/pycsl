r"""Test 3510 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. `{0: 1, -0: 2}[0]`: `-0` is a non-literal key equal to 0; CPython 2; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {0: 1, -0: 2}
    return d[0]

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f() != 1, f()
