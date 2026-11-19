# pycsl-expected: PASS
"""1286 - (#49) ROUTE #100 CAPABILITY ARM. This one MUST PROVE, and it is what separates a
REPAIR from a BLANKET REFUSAL.

Same classes as 1285, but the caller is GUARDED by `#@ requires k >= 0`, so the callee's
`raises ValueError when n < 0` condition is provably unreachable and the `no_exception`
obligation IS dischargeable. After the repair the caller emits exactly what the
free-function path has always emitted:

    begin assert { not ((k < 0)) }; try (self_checked_abs_1 k) with ValueError -> absurd end end

and the `assert` discharges from the precondition.

>>> THIS FILE ALSO PASSED BEFORE THE REPAIR, AND THAT PASS WAS WORTH NOTHING: no obligation
>>> was emitted at all, so it passed for the same (absent) reason 1285 did. A guard whose
>>> population is empty looks exactly like a guard that passed. What changed is that the
>>> pass is now EARNED.

The rejected alternative repair is why this witness exists. Transmitting the callee's
`raises` onto the abstract val (spiked, and it does close 1285) emits
`raises { ValueError -> true }` - UNCONDITIONAL - which destroys this capability: the
guarded caller stops proving too. The landed repair reuses the wrap, which carries the
callee's CONDITION, so it refuses only what is actually unprovable.
"""
_ = 0  # anchor


class Helper:
    def __init__(self) -> None:
        self.z: int = 0

    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ raises ValueError when n < 0
    def checked_abs(self, n: int) -> int:
        if n < 0:
            raise ValueError
        return n

    #@ requires k >= 0
    #@ no_exception ValueError
    #@ assigns \nothing
    def caller(self, k: int) -> int:
        return self.checked_abs(k)
