r"""Test 1308 — ROUTE #112 negative witness: a NON-EMPTY dict literal in ARGUMENT position
lowered to the EVERYWHERE-EMPTY MAP.

FALSE OF THE PROGRAM: `g({1: 5})` returns 1 (CPython). At the parent commit `f`'s
`\result == 0` PROVED (rc=0): `DictLitExpr`'s faithful `map_update_some` chain is gated on
the ENCLOSING function returning a map, every other non-empty literal fell through to
`(const (None: option int))`, and route #86's map-param coercion kept that by PREFIX. The
fallback for a literal WITH KEYS is now the unconstrained `any_map`: the emission is
`(g (any_map ()))` and the claim is refused on `f`'s postcondition.
"""
# pycsl-expected: FAIL
from typing import Dict

#@ ensures (1 in d) ==> \result == 1
#@ ensures (not (1 in d)) ==> \result == 0
def g(d: Dict[int, int]) -> int:
    if 1 in d:
        return 1
    return 0

#@ ensures \result == 0
def f() -> int:
    return g({1: 5})
