r"""Test 3529 -- gen #37 route #297 (expected PASS): the TRUE twin of 3515: with `requires k == 0`,
`{0: 1, k: 2}[0] == 2` proves from the faithful map once the fold declines.
"""
# pycsl-expected: PASS
from typing import List, Dict, Set, Tuple, Optional

#@ requires k == 0
#@ ensures \result == 2
#@ assigns \nothing
def f(k: int) -> int:
    d: Dict[int, int] = {0: 1, k: 2}
    return d[0]

if __name__ == "__main__":
    assert f(0) == 2
