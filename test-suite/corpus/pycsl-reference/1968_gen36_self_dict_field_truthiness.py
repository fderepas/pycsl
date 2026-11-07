r"""Test 1968 — gen #36 (expected PASS): the truthiness of a DIRECT `self.<f>` read of a
`Dict` record field of a plain class. The field is declared `map string (option int)`, and
`if not self.d:` lowered to the int coercion `self.d <> 0` (an L3-tc rejection). It is now
the field's non-emptiness, `map_nonempty` (`result <-> exists k. Map.get m k <> None`):
after a store the field is non-empty, after a reset it is empty. Twin: 1969 (must FAIL).
"""
# pycsl-expected: PASS
from typing import Dict


class Registry:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {}

    #@ ensures \result == 1
    #@ assigns self.d
    def put(self, k: str) -> int:
        self.d[k] = 1
        if not self.d:
            return 0
        return 1

    #@ ensures \result == 0
    #@ assigns self.d
    def reset(self) -> int:
        self.d = {}
        if self.d:
            return 1
        return 0
