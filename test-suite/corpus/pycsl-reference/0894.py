"""Test 0894 — NEGATIVE twin of 0893 (`alternatives` non-vacuity floor). # pycsl-expected: FAIL

The soundness floor for the `alternatives` node-list projection exercised by
0893, split into two cheap non-recursive claims that must BOTH stay unproven:

  * `is_constructor_unsound` — `.get("pattern")` lowers to the GENUINE `kind_of`
    discriminant, so the `Constructor` arm is REACHABLE and `\result == False`
    is false of the faithful lowering.
  * `alt_count_unsound` — `.get("alternatives", [])` is a GENUINE `args_of` node
    list whose length is not pinned to zero, so `\result == 0` is false of the
    faithful lowering.

If either ever PASSES, the `kind_of` discriminant has collapsed to a constant or
the `alternatives` list has become vacuously empty — which would let an
emitter-shaped `Or`-pattern walker "prove" it never sees a constructor
alternative, the exact unsoundness the lock guards (severity-1).
"""
# pycsl-expected: FAIL
from typing import Any, Dict
from dataclasses import dataclass

ExprIR = Dict[str, Any]


def mutable_state(cls): return cls


@mutable_state
@dataclass
class PatternWalker:
    _seen: int = 0

    #@ requires True
    #@ ensures \result == False
    #@ assigns \nothing
    def is_constructor_unsound(self, pat: ExprIR) -> bool:
        if pat.get("pattern") == "Constructor":
            return True
        return False

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def alt_count_unsound(self, pat: ExprIR) -> int:
        alts = pat.get("alternatives", [])
        return len(alts)
