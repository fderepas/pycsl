r"""Test 2277 — route #242 (expected FAIL): a `let function` over a `\trusted` callee whose contract
does NOT pin its result. `roll` is a bodyless `val` (`1 <= \result <= 6`), so its Python body is unseen
and may answer differently per call (it does: `random.randint`). `one` (no writes) only forwards
`roll()`; as a `let function` it froze that answer, so `one() - one() == 0` PROVED at f0fc0201 while
CPython `m()` is nonzero whenever the two rolls differ. `one` is now a plain `let` (two calls, two
values within the contract): unproved.
"""
# pycsl-expected: FAIL
import random


#@ \trusted reviewer: route-242-witness
#@ ensures \result >= 1 and \result <= 6
#@ assigns \nothing
def roll() -> int:
    return random.randint(1, 6)


#@ assigns \nothing
def one() -> int:
    return roll()


#@ ensures \result == 0
#@ assigns \nothing
def m() -> int:
    return one() - one()
