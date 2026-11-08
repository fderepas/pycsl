r"""Test 3222 — gen #37 ch28 (expected FAIL): 3220 with a WRONG value claim: the absent node's kind is
"", not "Var". Must not prove (guards against the sentinel being modelled as an arbitrary node).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Picker:
    depth: int = 0

    #@ requires not c
    #@ ensures \result == "Var"
    def absent_kind(self, node: "ExprIR", c: bool) -> str:
        a = node if c else {}
        return a.get("type", "")


if __name__ == "__main__":
    assert Picker().absent_kind({"type": "Var", "name": "x"}, False) == ""
    print("ok")
