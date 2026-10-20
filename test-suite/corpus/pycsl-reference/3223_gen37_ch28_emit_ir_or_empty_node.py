r"""Test 3223 — gen #37 ch28 (expected PASS): `<emit_ir> or {}` is value-preserving: the selected operand, with
the `{}` operand lowered to the absent sentinel `(IrOther "")` (Python dict truthiness =
`kind_of <> ""`). At base the `{}` lowered to an int and the `or` took the int path
(`__or_l <> 0`), an L3-tc failure. With `c` false, `a` is the empty node, so `a or {}` is the
empty node and its kind is "". Twin: 3224 (must FAIL).
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
    def absent_kind_or(self, node: "ExprIR", c: bool) -> str:
        a = node if c else {}
        b = a or {}
        return b.get("type", "")


if __name__ == "__main__":
    assert Picker().absent_kind_or({"type": "Var", "name": "x"}, False) == ""
    print("ok")
