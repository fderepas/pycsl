"""Test 0881 — tier3-p1 complete-EXPR-family recognizer lock (NEGATIVE twin of 0880). # pycsl-expected: FAIL

The soundness floor for the `is_sub` constructor discriminant exercised by 0880.
Because `node.get("type") == "Subscript"` lowers to the GENUINE match-based
discriminant `(is_sub node)`, the `Subscript` arm is reachable — a Subscript node
takes it and returns 0. The contract CLAIMS `\result == 1` unconditionally, which
is FALSE of the faithful lowering (a Subscript node reaches the `return 0` arm), so
it must remain UNPROVEN.

If this test ever PASSES, the `is_sub` discriminant has collapsed to a vacuous
`false` (no node ever satisfies it) — the exact unsoundness the `kind_of` catch-all
(`IrOther "Subscript"`) would introduce if the discriminant were not a real
constructor test — letting the unreachable `return 0` be ignored (severity-1).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

ExprIR = Dict[str, Any]


#@ ensures \result == 1
def subscript_discriminant_unsound(node: ExprIR) -> int:
    if node.get("type") == "Subscript":
        return 0
    return 1
