"""1169 — ROUTE #70 NEGATIVE: a callee's postcondition propagated without its precondition.

The dotted-call stub declared `val self_pos_only_1 (x0: int) : int ensures { result > 0 }`
— the callee's ensures, with NO requires — alongside the correct `val c__pos_only ...
requires { x > 0 }`. The CALL SITE used the first. CPython returns -5.

Dropping BOTH clauses would be fail-closed (an opaque stub concludes nothing); keeping the
postcondition without the precondition is the one combination that is always unsound.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class C:
    tag: int = 0

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires x > 0
    #@ ensures \result > 0
    #@ assigns \nothing
    def pos_only(self, x: int) -> int:
        return x

    #@ requires True
    #@ ensures \result > 0
    #@ assigns \nothing
    def caller(self) -> int:
        return self.pos_only(-5)
