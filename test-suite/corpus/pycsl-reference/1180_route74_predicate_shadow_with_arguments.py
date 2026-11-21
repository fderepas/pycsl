"""1180 — ROUTE #74 SECOND CARRIER: the same defect on the ARGUMENTS path.

The twelve names include `startswith`/`endswith`, which take arguments, and that path emits
`val self_startswith_1 (x0: int) : int ensures { ((result = 0) || (result = 1)) }` — the
argument is coerced to an int and the receiver is still erased. Measured with the guard
removed: this PROVED. CPython answers 9.

It is kept separate from 1178 because a guard that closed only the zero-argument spelling
would leave this one open, and that is the exact shape of failure this campaign has hit
repeatedly.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0


class C:
    #@ ensures \result == 9
    #@ assigns \nothing
    def startswith(self, n: int) -> int:
        return 9

    #@ ensures \result <= 1
    #@ assigns \nothing
    def g(self) -> int:
        return self.startswith(3)
