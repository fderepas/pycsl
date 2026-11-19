r"""Test 2061 — gen #36 (expected PASS): an EMPTY `{}` literal stored into a `Dict[str, str]`
self FIELD of a plain class (no `@mutable_state`). At base the store lowered to the INT empty
map `(const (None: option int))` against the field's `map string (option string)` — a Why3
type error (refused). It is now `(const None)`, the same everywhere-None map with its types
inferred from the field, so the reset's real consequence (`"k" in self.d` is False) proves.
Twins: 2062 / 2063 (must FAIL).
"""
# pycsl-expected: PASS
from typing import Dict


class Table:
    def __init__(self) -> None:
        self.d: Dict[str, str] = {}

    #@ ensures \result == False
    #@ assigns self.d
    def reset(self) -> bool:
        self.d = {}
        return "k" in self.d
