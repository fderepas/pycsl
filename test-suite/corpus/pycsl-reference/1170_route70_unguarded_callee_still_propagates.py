"""1170 — ROUTE #70 POSITIVE CONTROL: an UNGUARDED callee still exports its postcondition.

The repair withholds ensures propagation only when the callee has a NON-TRIVIAL precondition
that cannot be rendered at the call site. A callee with no precondition must still hand its
postcondition to the caller — otherwise the fix is a blanket ban on contract propagation
through dotted calls, and 1169 would pass for the wrong reason.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class C:
    tag: int = 0

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures \result > 0
    #@ assigns \nothing
    def always_pos(self, x: int) -> int:
        return 1

    #@ requires True
    #@ ensures \result > 0
    #@ assigns \nothing
    def caller(self) -> int:
        return self.always_pos(-5)
