# pycsl-expected: FAIL
"""1285 - (#49) ROUTE #100 EXPLOIT ARM: a `#@ no_exception E` on a METHOD was proved with
NO OBLIGATION AT ALL.

`caller` claims `#@ no_exception ValueError` and calls a callee declaring
`#@ raises ValueError when n < 0` with nothing constraining the argument. As FREE FUNCTIONS
(1287) the identical pair is correctly REFUSED. As METHODS of one class, MEASURED AT
a32ec69e, this file reported `Verification SUCCESS! All contracts formally proven.` - and
CPython raises: `Helper().caller(-1)` -> ValueError.

MECHANISM, read off the emitted WhyML rather than inferred. The free-function path emits

    begin assert { not ((k < 0)) }; try (checked_abs k) with ValueError -> absurd end end

and the method path emitted the bare

    (self_checked_abs_1 k)

`_wrap_call_with_callee_raises_assert` had exactly ONE call site - the module-function path
- and is keyed on the IR function name, so `self.checked_abs(k)` never reached it and the
caller's `no_exception` set was discharged by nobody.

>>> AN ABSTRACTION THAT IS CONSERVATIVE FOR WHAT A CALLER MAY **ASSUME** IS PERMISSIVE FOR
>>> WHAT A CALLER MUST **DISCHARGE**. The abstract val already carries the callee's
>>> `ensures` (measured), so this path VISIBLY carries a contract and reads as sound. The
>>> transmission set had been enumerated as "what the caller may assume" - the half that
>>> HELPS the caller. Losing a postcondition costs a proof; losing an effect obligation
>>> costs the CHECK.

Must FAIL.
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

    #@ requires 1 == 1
    #@ no_exception ValueError
    #@ assigns \nothing
    def caller(self, k: int) -> int:
        return self.checked_abs(k)
