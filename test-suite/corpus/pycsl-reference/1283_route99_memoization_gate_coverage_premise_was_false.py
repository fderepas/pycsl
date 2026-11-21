# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1283 — (#49) ROUTE #99: THE ORDERING HALF COULD NOT BE ISOLATED BY A WITNESS, AND THIS
FILE RECORDS WHY, PLUS THE FENCE THAT BLOCKS THE ATTEMPT.

Route #99 had TWO independent narrowings, and the repair needed both:
  (1) the mutated-field collector admitted a write only when spelled `self.<f>`;
  (2) the check ran at the end of `visit_ClassDef`, so a MODULE-LEVEL function defined
      after the class was not yet in `program_ir["functions"]`.
Measured directly: fixing (1) alone left 1282 still PROVING; only moving the check to the
end of `visit_Module` closed it. So both are real.

I TRIED TO BUILD A WITNESS ISOLATING (2) ALONE AND COULD NOT — both attempts are blocked by
UNRELATED, LOUD, FAIL-CLOSED fences, and each was measured rather than assumed:

  * THIS FILE's shape — mutator declared BEFORE the class, so it is visible whatever the
    hook, leaving only the receiver test in play. It needs the forward annotation
    `def bump(c: "C")`, and at a32ec69e that FAILS for a reason that has nothing to do with
    UB-7.7: the parameter is emitted as `int` because the class is not yet declared, and
    Why3 rejects it —
        This expression has type int, but is expected to have type PyCSL_Program.c
  * the other attempt — a module-level mutator AFTER the class whose parameter is *named*
    `self`, so the old receiver test would pass and only the ordering would hide it. Also
    refused at baseline, also for an unrelated reason:
        unbound function or predicate symbol 'self'
    (`self` in a contract is special-cased to a method's receiver).

>>> A CONTROL THAT FAILS IS A CLAIM ABOUT THE CONTROL UNTIL YOU READ *WHICH GOAL* FAILED.
>>> Both of these look like "the gate caught it" in a pass/fail column and neither is. The
>>> campaign rule caught them: this file was ORIGINALLY committed claiming to isolate the
>>> ordering half, and reading the baseline failure reason is what showed it does not.

So the route's witness is 1282 (which requires BOTH fixes), and this file stands as the
standing record of the two fences. It must FAIL — today because the repaired UB-7.7 gate
refuses it, at baseline because of the forward-reference typing above. If it ever XPASSes,
BOTH the forward-annotation fence and the memoization gate have changed and this file must
be re-derived rather than re-blessed.
"""
_ = 0  # anchor
from functools import cached_property


#@ requires c.a >= 0
#@ assigns c.a
#@ ensures c.a == \old(c.a) + 1
def bump(c: "C") -> None:
    c.a = c.a + 1


#@ class invariant self.a >= 0
class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures \result == self.a
    #@ assigns \nothing
    @cached_property
    def total(self) -> int:
        return self.a
