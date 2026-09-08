"""Test 1090 — ROUTE #46 control: a STRAIGHT-LINE rebinding keeps its precision.

TRUE OF THE PROGRAM: Python returns 0 (`x` is 5 at the guard, and `5 == 0` is False).

The pre-scan that closes 1089 is flow-INSENSITIVE, so on its own it would mark this `x`
ambiguous too and make a guard the model gets exactly right undecidable. It does not,
because the scan carries a NESTING DEPTH: when every binding of a name sits at the TOP
LEVEL of the function body, emission order IS execution order and the existing linear
record is already exact. Ambiguity needs a CONDITIONAL binding. This file is what holds
that half of the design.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = None
    x = 5
    if x == 0:
        return 7
    return 0


if __name__ == "__main__":
    assert f() == 0
