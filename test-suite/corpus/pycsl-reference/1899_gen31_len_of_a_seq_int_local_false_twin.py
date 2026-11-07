r"""Test 1899 — gen #31 FALSE TWIN for 1898 (expected FAIL): `Seq.length` is not a free pass.

Byte-identical to 1898 but for `#@ ensures \result >= 1`, which is FALSE — `.get(k, [])`
answers the EMPTY seq for an absent key and `Seq.length Seq.empty` is 0. The repair makes
`len()` of a `seq int` local LOWER; it does not make claims about the length true.
"""
# pycsl-expected: FAIL
from typing import Dict, List


def mutable_state(cls):
    return cls


_ = 0  # anchor


@mutable_state
class C:
    def __init__(self) -> None:
        self.m: Dict[int, List[int]] = {}

    #@ ensures \result >= 1
    def arity(self, k: int) -> int:
        fp = self.m.get(k, [])
        return len(fp)
