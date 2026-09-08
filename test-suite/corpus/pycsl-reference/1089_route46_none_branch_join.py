"""Test 1089 — ROUTE #46 negative witness: THE `None` RECORD DID NOT SURVIVE A BRANCH JOIN.

FALSE OF THE PROGRAM: `None == 0` is False in Python, so `f(1)` returns 0.

Route #44 made a `None`-bound local's reads the opaque `pycsl_none`, and the record it keys
on is LINEAR — written when the assignment is EMITTED and cleared when the name is rebound.
Emission walks the `then` body and then the `else` body, so the `else`'s `x = 5` cleared the
record the `then`'s `x = None` had set and the guard after the join read the ordinary `!x`,
which the model still holds at the literal `0`. `\\result == 7` PROVED at 90fed0c9 and at
every earlier commit.

THE REPAIR IS A PRE-SCAN, and its shape is the lesson: `bool(x) is False` and `x is the
None singleton` are PATH facts, and a flow-INSENSITIVE record cannot carry a path fact. So
the function body is walked ONCE before emission and a name bound to `None` on some path
and to something else on another is marked AMBIGUOUS for the whole function — its value
opaque, its truthiness undecided. 1090 is the control that keeps the flow-insensitivity
from costing anything it need not.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires c > 0
#@ ensures \result == 7
#@ assigns \nothing
def f(c: int) -> int:
    if c > 0:
        x = None
    else:
        x = 5
    if x == 0:
        return 7
    return 0


if __name__ == "__main__":
    assert f(1) == 0
