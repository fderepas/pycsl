r"""Test 3221 — gen #37 ch28 (expected FAIL): 3220 without `requires not c`: when `c` is true the ternary
selects the REAL node, whose kind is arbitrary, so `\result == ""` is false in CPython
(`{"type": "Var"}` gives "Var") and must not prove. Guards against the `{}` arm leaking into the
`then` arm (a model that always read the sentinel would prove this).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Picker:
    depth: int = 0

    #@ ensures \result == ""
    def absent_kind(self, node: "ExprIR", c: bool) -> str:
        a = node if c else {}
        return a.get("type", "")


if __name__ == "__main__":
    assert Picker().absent_kind({"type": "Var", "name": "x"}, True) == "Var"
    print("ok")
