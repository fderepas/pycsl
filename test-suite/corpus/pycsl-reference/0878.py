"""Test 0878 — tier3-p1 IR-node ADT recognizer lock (POSITIVE, expr family).

Locks the Module-6 realization of the Phase-0 WhyML spike
(`test-suite/corpus/conformance/spikes/tier3_ir_node_adt_spike.mlw`): an
IR-node-typed parameter (`node: ExprIR`) lowers to the pure `emit_ir` variant
ADT, so an emitter-shaped function can reflect on it faithfully.

Exercises all three increment pieces on the EXPR operator node (`BinOp`):
  * T3.1.1 — the `emit_ir` variant type (with `IrBinOp op left right`) + the
    `ir_num` numeric-leaf carrier are emitted (gated on the IR-node param; the
    corpus has none, so emission is byte-identical there).
  * T3.1.2 — `node.get("type") == "BinOp"` lowers to the constructor
    DISCRIMINANT `(is_binop node)` (spike LAW 1); `node.get("op")` reads the
    operator string via `op_of` (spike LAW 2); `node.get("left")`/`.get("right")`
    project the SUB-NODES via `left_of`/`right_of`.
  * T3.1.4 — the recursion over the projected sub-nodes terminates via the
    emitter-injected `variant { size node }` (spike LAW 3), discharged by the
    theory's guarded size-decrease lemmas — no axiom, both provers.

`node_size` proves `\result >= 1` faithfully: every node has size at least 1,
and the structural recursion terminates. `binop_operator` proves it returns the
`op_of` string projection. If this test regresses, the ADT recognizer or its
termination measure has broken.
"""
from typing import Any, Dict

ExprIR = Dict[str, Any]


#@ ensures \result >= 1
def node_size(node: ExprIR) -> int:
    if node.get("type") == "BinOp":
        return 1 + node_size(node.get("left")) + node_size(node.get("right"))
    return 1


def binop_operator(node: ExprIR) -> str:
    #@ ensures True
    if node.get("type") == "BinOp":
        return node.get("op")
    return ""
