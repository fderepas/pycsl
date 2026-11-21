r"""Test 1897 — gen #31 FALSE TWIN for 1896 (expected FAIL): resolving the type is not a free pass.

Byte-identical to 1896 but for `#@ ensures \result >= 1`, which is FALSE — `self.m.get(name, [])`
answers the empty list for an absent key, and `len([])` is 0. The repair makes the field's
value type REACHABLE; it does not make claims about the field true. Without this twin,
"1896 verifies" would only say the file type-checks.
"""
# pycsl-expected: FAIL
from typing import Dict, List


def mutable_state(cls):
    return cls


_ = 0  # anchor


@mutable_state
class C:
    def __init__(self, m: Dict[str, List[str]]) -> None:
        self.m = m

    #@ ensures \result >= 1
    def arity(self, name: str) -> int:
        fp = self.m.get(name, [])
        return len(fp)
