r"""Test 3224 — gen #37 ch28 (expected FAIL): 3223 with `requires c`: `a` is the REAL node, `a or {}`
selects it (a real node is truthy), and its kind is arbitrary, so `\result == ""` must not prove
(CPython: "Var"). Guards against the `or` collapsing to the `{}` operand.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Picker:
    depth: int = 0

    #@ requires c
    #@ ensures \result == ""
    def absent_kind_or(self, node: "ExprIR", c: bool) -> str:
        a = node if c else {}
        b = a or {}
        return b.get("type", "")


if __name__ == "__main__":
    assert Picker().absent_kind_or({"type": "Var", "name": "x"}, True) == "Var"
    print("ok")
