"""Test 0747 — PyCSL Annotation Reference (dict-literal emit_ir construction).

Exercises the dict-literal→emit_ir feature: a method that builds an IR node with dict literals
(`{"type": "Var", ...}` / `{"type": "Attribute", "object": node, ...}`) and returns it is typed
`emit_ir` (the sum `IrVar`/`IrAttr`), NOT the `map int (option int)` its `-> Dict[str, Any]`
annotation would imply. The reassigned local `node` is an `emit_ir` ref (`ref (IrOther "")`), each
literal lowers to a constructor, and the return type is inferred `emit_ir`."""
from typing import Dict, Any


def mutable_state(cls):
    return cls


@mutable_state
class NodeBuilder:
    #@ requires True
    #@ ensures True
    def build(self, root: str, attr: str) -> Dict[str, Any]:
        node: Dict[str, Any] = {"type": "Var", "name": root}
        node = {"type": "Attribute", "object": node, "attr": attr}
        return node


if __name__ == "__main__":
    b = NodeBuilder()
    n = b.build("x", "f")
    assert n["type"] == "Attribute"
