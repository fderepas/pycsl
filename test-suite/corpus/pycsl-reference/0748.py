"""Test 0748 — PyCSL Annotation Reference (method tuple-return with emit_ir/string slots).

A `@mutable_state` record method returning a 2-tuple whose slots are an `emit_ir` sub-node
(`node["value"]` → svalue_of) and a `string` discriminant (`node.kind` → kind_of) has its return
type inferred `(emit_ir, string)` — not the homogeneous `(int, int)` default. A caller that unpacks
it (`sub, kind = self.split(node)`) types `sub` as `emit_ir` and `kind` as `string`."""
from typing import Any, Tuple
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Splitter:
    depth: int = 0

    #@ requires True
    #@ ensures True
    def split(self, node: "ExprIR") -> Tuple[Any, str]:
        return node["value"], node.kind

    #@ requires True
    #@ ensures True
    def kind_of_sub(self, node: "ExprIR") -> str:
        sub, kind = self.split(node)
        return kind
