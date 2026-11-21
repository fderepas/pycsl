"""Test 1085 — ROUTE #50 negative witness (a): `x is None` ON A STRING LOCAL WAS THE
LITERAL `false`.

FALSE OF THE PROGRAM: Python takes the `is None` branch and `m(-1, "x")` returns 0.

`s` is bound to `None` and then REBOUND on a path the precondition excludes, so the linear
`_erased_truthy_locals` record is cleared by the time the guard is emitted and the
comparison fell to the `@mutable_state` string arm — which answered `false` for EVERY
string operand, whatever the binding. That is not an approximation of the branch, it is the
DELETION of one: `if false then <the None path>` makes the path Python actually takes
unreachable, so the contract was proved over a STRICT SUBSET of the reachable states. At
the parent commit 90fed0c9 `\\result == 7` PROVED.

The decorator is load-bearing and 1088 is the control that says so: without
`@mutable_state` the same file fails closed, because the string-local classification that
feeds this arm is `@mutable_state`-gated.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires c < 0
    #@ requires t == "x"
    #@ ensures \result == 7
    def m(self, c: int, t: str) -> int:
        s = t
        s = None
        if c > 0:
            s = t
        if s is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.m(-1, "x") == 0
