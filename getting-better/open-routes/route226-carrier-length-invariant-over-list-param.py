"""ROUTE #226 CARRIER (gen #37) — a `\\length` invariant over a LIST field bound to an
`__init__` parameter, with no `#@ requires`, is ASSUMED.

This file PROVED A FALSE CONTRACT until increment 2c (`#@ no_exception \\all` on `first`), which is why it
lives here and not in the corpus. `bin/check-open-route-carriers.py` runs it and asserts the
verdict this route's record states.

The gen #37 int-field projection states the constructor goal over the INT fields an
invariant reads (`self.x = x` beside a `str` / `List` field). This invariant reads a LIST
field (`\\length(self.xs)`), so the goal cannot be stated in the int-only form and NO goal is
emitted; every method assumes `Array.length xs >= 1` and the in-bounds VC of `self.xs[0]`
discharges. CPython: `D([]).first()` raises IndexError.

WHY NOT REFUSE (measured, route #226 REPAIR gen #37): 25 classes have this shape with no
`#@ requires` (the token-cursor / parser family, `Parser(toks)` under
`\\length(self.toks) >= 1`: 0900, 0925-0935, 0966, 1190, 1681/1682, 1690, 2220 and the
mirrors `pure_ast._Parser` / `proof2why3/parser._Parser` among them), 17 of them in PASS
files, so a refusal is not inert. The
honest goal quantifies an `array` binder (`forall xs: array int. inv`) and needs `#@ requires
len(xs) >= 1` on those constructors — the next increment.

CLOSED (gen #37, increment 2c): the goal now binds `xs` as an array,
`forall xs : array int. xs = xs -> (Array.length xs >= 1)`, and FAILS. EXPECTED: FAILED
(asserted by `bin/check-open-route-carriers.py`); corpus witness 5100.
"""
from typing import List


#@ class invariant \length(self.xs) >= 1
class D:
    def __init__(self, xs: List[int]) -> None:
        self.xs = xs

    #@ no_exception \all
    #@ assigns \nothing
    def first(self) -> int:
        return self.xs[0]


if __name__ == "__main__":
    try:
        D([]).first()
    except IndexError:
        print("IndexError")
