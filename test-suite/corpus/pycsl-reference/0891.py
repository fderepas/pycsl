"""Test 0891 — option-of-record projection: Optional[TypedDict].get(k) → Some-arm field read.

boundary-1 G1 extension (option-of-record projection). An `Optional[<record>]` param
monomorphizes to the native `option <record>` — NOT `Optional[Any]`: the record Union arm
SURVIVES GT1 (a `TypedDict`/`@dataclass` arm is a concrete record, not a bare `Any`), so the
option's `Some` payload is the real record. After the `if r is None:` guard, `r.get("k")`
projects the field FROM THE Some ARM:

    (match r with Some _v -> _v.<label> | None -> <default> end)

The `is None` test lowers to the FAITHFUL option match `(match r with None -> true | Some _ ->
false end)` — both arms reachable — so the field-reading Some arm is NON-VACUOUS (the body does
NOT collapse to a None-only "proof"). A str field routes its literal comparison through
`str_eq_op`. If this regresses, the option-of-record projection (front-end record-arm survival
or the emitter Some-arm projection) broke.
"""
from typing import Optional, TypedDict


class Node(TypedDict):
    kind: str
    op: str


#@ requires True
#@ ensures True
#@ assigns \nothing
def is_compare(node: Optional[Node]) -> bool:
    if node is None:
        return False
    k = node.get("kind", "")
    if k == "Compare":
        return True
    if k == "BinOp" and node.get("op", "") == "and":
        return True
    return False
