r"""Test 3220 — gen #37 ch28 (expected PASS): the empty-dict `{}` arm of an emit_ir ternary, `node if c else {}`,
is the absent sentinel `(IrOther "")`. At base the arm lowered to an int and the ternary failed
L3-tc (`int` where `emit_ir` is expected). With `c` false the value is the empty node, whose
`.get("type", "")` is "" (CPython: `{}.get("type", "")` is ""). Twins: 3221, 3222 (must FAIL).
"""
# pycsl-expected: PASS
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Picker:
    depth: int = 0

    #@ requires not c
    #@ ensures \result == ""
    def absent_kind(self, node: "ExprIR", c: bool) -> str:
        a = node if c else {}
        return a.get("type", "")


if __name__ == "__main__":
    assert Picker().absent_kind({"type": "Var", "name": "x"}, False) == ""
    print("ok")
