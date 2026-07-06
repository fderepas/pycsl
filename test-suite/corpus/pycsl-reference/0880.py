"""Test 0880 — tier3-p1 COMPLETE EXPR-family IR-node ADT recognizer lock (POSITIVE).

Increment 2 of the Phase-1 realization (`triage-ranked-tcb-tier3.md` T3.1.1/2/4):
the BinOp recognizer (test 0878) is extended to the REST of the fixed-arity expr
family. An IR-node-typed parameter (`node: ExprIR`) lowers to the pure `emit_ir`
variant ADT, so an emitter-shaped function reflecting on its own IR self-verifies.

Exercises every newly-covered kind's discriminant + projection + terminating
recursion (all facts supplied with NO axiom, both provers):
  * `.get("type") == "Subscript"` -> `(is_sub node)`; `.get("value")`/`.get("index")`
    -> the SUB-NODE projections `svalue_of`/`sindex_of`; recursion terminates via
    the theory lemmas `size_svalue_dec`/`size_sindex_dec`.
  * `.get("type") == "Attribute"` -> `(is_attribute node)`; `.get("object")` ->
    the SUB-NODE `object_of`; recursion terminates via `size_object_dec`.
  * `.get("type") == "BinOp"` -> `(is_binop node)`; `.get("left")`/`.get("right")`
    -> `left_of`/`right_of` (from test 0878, still holds).
  * The LEAF discriminants `.get("type") == "Var" / "Number" / "String" / "FieldGet"`
    -> `(is_var node)` / `(is_num node)` / `(is_str node)` / `(is_fieldget node)`
    (each a real match-based bool, not a `kind_of` string compare).

`expr_size` proves `\result >= 1` faithfully: every node has size at least 1 and
the structural recursion over the projected sub-nodes terminates. If this test
regresses, a discriminant, a sub-node projection, or a size-decrease lemma broke.
"""
from typing import Any, Dict

ExprIR = Dict[str, Any]


#@ ensures \result >= 1
def expr_size(node: ExprIR) -> int:
    if node.get("type") == "BinOp":
        return 1 + expr_size(node.get("left")) + expr_size(node.get("right"))
    if node.get("type") == "Subscript":
        return 1 + expr_size(node.get("value")) + expr_size(node.get("index"))
    if node.get("type") == "Attribute":
        return 1 + expr_size(node.get("object"))
    return 1


def is_leaf_kind(node: ExprIR) -> bool:
    #@ ensures True
    if node.get("type") == "Var":
        return True
    if node.get("type") == "Number":
        return True
    if node.get("type") == "String":
        return True
    if node.get("type") == "FieldGet":
        return True
    return False
