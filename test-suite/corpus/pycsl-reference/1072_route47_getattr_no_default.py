"""Test 1072 — ROUTE #47 negative witness (c): the NO-DEFAULT form, where Python has no
value at all.

FALSE OF THE PROGRAM: `getattr(c, "missing")` raises `AttributeError`. There is no value,
so no contract about one can be true.

`if len(args_ir) <= 2: return "0"` fabricated a zero out of nothing, and the guard then
decided on it. At the parent commit d7ce974c `\\result == 7` PROVED. This is the worst of
route #47's three: the other two model a real Python value badly, this one models a value
that does not exist.

The repair makes it OPAQUE rather than REFUSED, and that is a measurement rather than a
preference: `bin/check-getattr-erasure.py` reports ABSENT 7 / UNKNOWN 19 sites, and for an
object of UNKNOWN static type the attribute may well exist, so a refusal would break
nineteen sites to state something true of at most seven. RESIDUE, stated: opacity models
"some value" where Python has none, so a contract about the `AttributeError` itself is
still not expressible.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures True
    def __init__(self) -> None:
        self.x = 1


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C()
    d = getattr(c, "missing")
    if d == 0:
        return 7
    return 0
