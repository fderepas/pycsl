r"""Test 1712 — ROUTE #206 CONTROL: a total target MAY call a helper, as long as the helper
has a verified body.

Identical in shape to 1711 except `step` carries a real, verified body instead of
`#@ \trusted`. Route #206's refusal is about a BODYLESS function reachable from the target,
not about calling anything at all — if this file ever fails, the refusal has become a ban
on helper functions under a `total` policy.

THE TARGET'S POSTCONDITION DELIBERATELY DOES NOT DEPEND ON THE HELPER'S RESULT, and the
reason is worth recording because it is what made route #206 provable in the first place.
A `self.<method>(...)` call lowers to an abstract op, and the emission carries the callee's
contract onto that op ONLY when the callee is a bodyless `val`:

    val self_spin_1 (x0: int) : int          (* \trusted callee  *)
      ensures { (result >= 0) }              (* contract CARRIED  *)
    val self_step_1 (x0: int) : int          (* verified callee   *)
                                             (* NO contract       *)

So trusting a helper makes the caller STRONGER (it gains the helper's assumed
postcondition and loses the helper's termination VC), while verifying that same helper
leaves the caller with an uninterpreted result. A first version of this control returned
`self.step(n)` under `ensures \result >= 0` and FAILED for exactly that reason — an
unrelated propagation gap, not anything to do with route #206. A control that fails for
the wrong reason is worse than no control, so the call is made for its own sake and the
postcondition is independent of it.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ requires n >= 0
    #@ ensures \result >= 0
    def step(self, n: int) -> int:
        return n

    #@ requires n >= 0
    #@ no_exception \all
    #@ ensures \result == 0
    def parse(self, n: int) -> int:
        acc: int = self.step(n)
        return 0
