"""ROUTE #226 CARRIER — a `#@ class invariant` the CONSTRUCTOR never establishes.

This file PROVES A FALSE CONTRACT TODAY, which is why it lives here and not in the corpus:
`# pycsl-expected: FAIL` would be an XPASS (a red suite) and `PASS` would write "this false
proof is expected" into the reference set. `bin/check-open-route-carriers.py` runs it and
asserts the verdict this route's record states.

WHAT IT SHOWS. `__init__` sets `self.n = 0`; the invariant says `self.n >= 5`. The emitted
record is

    type c = { mutable n: int }
      invariant { (n >= 5) }
      by { n = 10 }

— the inhabitation witness is SYNTHESIZED FROM THE INVARIANT, and `__init__` is not emitted
at all, so nothing checks that the real constructor establishes it. Every method then gets
the invariant free, because a Why3 type invariant holds at every boundary for a value of
that type.

CLOSED. This carrier verified until the constructor obligation was emitted; it now
FAILS, which is the outcome the last paragraph below asked for. It is kept because
a closed carrier is the cheapest regression test a route has: if this file ever
verifies again, `goal _check_class_inv_c` has stopped being emitted for a paramless
literal constructor.

THE ROUTE IS NOT CLOSED. Three shapes still carry it and the live one is
`route226-carrier-invariant-from-a-constructor-parameter.py`, which IS registered.

WAS: SUCCESS. CPython: `C().get()` is 0, and `0 >= 5` is False.

WHEN THIS STOPS PROVING, the route is probably closed and
`route226-a-class-invariant-the-constructor-never-establishes.md` must be updated in the
SAME commit — that is the whole point of the carrier gate.
"""
_ = 0  # anchor


#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n
