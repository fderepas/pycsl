r"""Test 2004 — gen #36 (expected PASS): truthiness of a seq-promoted list local in a PLAIN
function (no `@mutable_state`). At base `if acc:` fell through to `Array.length !acc` — an
L3-tc rejection against the `seq string` ref; now it is `Seq.length !acc <> 0`, so the
taken branch is proved. Twin: 2005 (must FAIL).
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 1
#@ assigns \nothing
def go(k: int) -> int:
    acc: List[str] = []
    acc.append("a")
    if acc:
        return 1
    return 0
