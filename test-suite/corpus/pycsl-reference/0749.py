"""Test 0749 — PyCSL Annotation Reference (subscript-receiver .get projection).

A `.get("key")` whose receiver is an emit_ir ARRAY ELEMENT (`a[i].get("name")`, where `a = node.get
("args")` is an `array emit_ir`) projects over that element — `name_of`/`kind_of`/`func_of`/`value_of`
— exactly like a Var receiver. The receiver is carried in the Call's `receiver` field with a bare
`func == "get"`. A string-key projection also participates in `== "s"` comparisons (str_eq_op), and an
element's `.get("value")` reads its scalar string (`value_of`)."""
from typing import Any
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Reflector:
    depth: int = 0

    #@ requires True
    #@ ensures True
    def first_is_self(self, node: "ExprIR") -> int:
        a = node.get("args", [])
        if len(a) >= 1 and a[0].get("name") == "self":
            return 1
        return 0

    #@ requires True
    #@ ensures True
    def second_value(self, node: "ExprIR") -> str:
        a = node.get("args", [])
        if len(a) >= 2 and a[1].get("type") == "String":
            return a[1].get("value")
        return ""
