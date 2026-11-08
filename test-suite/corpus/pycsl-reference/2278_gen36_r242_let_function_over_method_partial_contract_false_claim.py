r"""Test 2278 — route #242 (expected FAIL): a `let function` over a METHOD call whose contract does
not pin its result. `c.roll()` lowers to the abstract op `c_roll_0` carrying only `1 <= \result <= 6`
(the method body, `1 + random.randint(0, 5) % 6`, is not linked at the call). `one` (no writes) forwards it; as a
`let function` it froze the answer per argument, so `one(c) - one(c) == 0` PROVED at f0fc0201 while
CPython `m(C())` is nonzero whenever the two rolls differ. `one` is now a plain `let`: unproved.
"""
# pycsl-expected: FAIL
import random


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 1 and \result <= 6
    #@ assigns \nothing
    def roll(self) -> int:
        return 1 + random.randint(0, 5) % 6


#@ assigns \nothing
def one(c: C) -> int:
    return c.roll()


#@ ensures \result == 0
#@ assigns \nothing
def m(c: C) -> int:
    return one(c) - one(c)
