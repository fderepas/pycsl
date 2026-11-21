"""Test 1087 — ROUTE #50 control: a LINEAR `None` binding keeps its DECIDED answer.

TRUE OF THE PROGRAM: Python returns 0.

The repair is not "make `is None` opaque". Where the binding is LINEAR the record says the
name IS the None singleton at the guard, and that is a fact rather than an approximation,
so the answer stays DECIDED — this file must keep proving. It is the control that separates
route #50's repair from a blunt refusal, and it is what the
`bin/check-singleton-constant-lowering.py` baseline entry for `_handle_binop` points at.

MEASURED, AND IT IS A COMPLETENESS GAIN: this file FAILED at the parent commit 90fed0c9 and
proves here. At the parent the read of a `None`-recorded local was the INT opaque
`pycsl_none` whatever the local's type, so on a string local it landed in `str_eq_op` and
Why3 type-rejected the file — fail-closed by type accident, not by design. Typing the
sentinel (`pycsl_none_str : string`) makes the honest answer expressible. Route #45 was the
first repair in this campaign to buy completeness as well as soundness; this is the second.
"""
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires t == "x"
    #@ ensures \result == 0
    def m(self, t: str) -> int:
        s = t
        s = None
        if s is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.m("x") == 0
