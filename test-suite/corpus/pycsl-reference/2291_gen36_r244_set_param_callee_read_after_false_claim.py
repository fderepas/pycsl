r"""Test 2291 — gen #36 r244 (expected FAIL): route #244, callee half. The method reads its own set parameter AFTER `s.add(1)`; CPython
returns True, so `\result == False` is FALSE. At cdac19a6 the add was erased to `()` and the
claim PROVED; the parameter is now shadowed (`let s = ref s in`) and the add is a real map
update, so the claim is unprovable.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    n: int = 0

    #@ ensures \result == False
    #@ assigns \nothing
    def m(self, s: Set[int]) -> bool:
        if 1 in s:
            return False
        s.add(1)
        return 1 in s


if __name__ == "__main__":
    assert C().m(set()) is True
