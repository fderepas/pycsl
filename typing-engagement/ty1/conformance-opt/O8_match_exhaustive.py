"""Static gate O8 (positive) — match exhaustiveness, both arms covered.

Spec clause O8 (optional-twoplane-spec.md §1.3): a `match` on a value of
type `Optional[X]` must cover both arms — there must be a reachable case
pattern that accepts a value of `X`, and a reachable case pattern that
accepts `None` (e.g. `case None:` or `case _:`). This driver covers
both arms of `Optional[int]` via `case int():` (the X arm) and `case _:`
(the catch-all, covering the None arm).

Expected (from spec): prove (exhaustive match over both constructors).
"""

from typing import Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(x: Optional[int]) -> int:
    match x:
        case int():
            return 1
        case _:
            return 0


if __name__ == "__main__":
    assert f(1) == 1
    assert f(None) == 0
    print("PASS")
