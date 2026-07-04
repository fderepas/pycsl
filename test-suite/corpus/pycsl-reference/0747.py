"""Test 0747 — PyCSL Annotation Reference (dict-literal emit_ir construction).

A `@mutable_state` record method that builds an IR node with dict literals
(`{"type": "Var", ...}` / `{"type": "Attribute", "object": node, ...}`) and returns it is typed
`emit_ir` (the sum `IrVar`/`IrAttr`), NOT the `map int (option int)` its `-> Dict[str, Any]`
annotation would imply. Requires a mutable-state RECORD (`@dataclass` + `@mutable_state`) — the
`emit_ir` model is gated on that; a plain class stays a heterogeneous map (vacuous)."""
from typing import Dict, Any
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class NodeBuilder:
    depth: int = 0

    #@ requires True
    #@ ensures True
    def build(self, root: str, attr: str) -> Dict[str, Any]:
        node: Dict[str, Any] = {"type": "Var", "name": root}
        node = {"type": "Attribute", "object": node, "attr": attr}
        return node
