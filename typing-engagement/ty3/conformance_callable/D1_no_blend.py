from typing import Callable


# D1 NO-BLEND (independence-based): the runtime `callable()` PRESENCE check
# must NOT discharge the static function-type obligation. This driver carries
# the PROVABLE static half: `f: Callable[[int], int]` is a WhyML arrow
# parameter, and the call `f(n)` type-checks because `n: int` (C2). The static
# obligation lives on a DIFFERENT plane from the runtime presence check.
#
# The divergence's NEGATIVE half is carried by `S5_c4_unprovable.py`: there a
# value postcondition on a bare callable is UNPROVABLE (the static plane refuses
# a value theorem the function-type does not justify), while the runtime
# `callable()` presence check would happily accept any callable — the runtime
# check cannot rescue the static claim. Together: the runtime presence check
# does NOT pass the static signature obligation and vice versa.

#@ requires n >= 0
#@ ensures \result == f(n)
def g(f: Callable[[int], int], n: int) -> int:
    return f(n)
