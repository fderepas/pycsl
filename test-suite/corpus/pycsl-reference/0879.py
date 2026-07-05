"""Test 0879 — tier3-p1 IR-node ADT recognizer lock (NEGATIVE twin of 0878). # pycsl-expected: FAIL

The soundness floor for the `is_binop` constructor discriminant exercised by
0878. Because `node.get("type") == "BinOp"` lowers to the GENUINE match-based
discriminant `(is_binop node)` (spike LAW 1), the `BinOp` arm is reachable — a
`BinOp` node takes it and returns 0. The contract CLAIMS `\result == 1`
unconditionally, which is FALSE of the faithful lowering (a `BinOp` node reaches
the `return 0` arm), so it must remain UNPROVEN.

If this test ever PASSES, the `is_binop` discriminant has collapsed to a vacuous
`false` (no node ever satisfies it) — the exact unsoundness the `kind_of`
catch-all (`IrOther "BinOp"`) would introduce if the discriminant were not a real
constructor test — letting the unreachable `return 0` be ignored (severity-1).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

ExprIR = Dict[str, Any]


#@ ensures \result == 1
def discriminant_unsound(node: ExprIR) -> int:
    if node.get("type") == "BinOp":
        return 0
    return 1
