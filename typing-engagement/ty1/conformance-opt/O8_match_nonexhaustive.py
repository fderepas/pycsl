"""Static gate O8 (negative) — match non-exhaustiveness must FAIL.

Spec clause O8 (optional-twoplane-spec.md §1.3): a `match` on a value of
type `Optional[X]` must cover both arms. This driver covers only the
`int` arm of `Optional[int]` — the `None` arm is uncovered (no
`case None:` and no `case _:`). The match is non-exhaustive and must be
a static error.

Expected (from spec): FAIL (non-exhaustive match is a static error).
"""

from typing import Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(x: Optional[int]) -> int:
    match x:
        case int():
            return 1


if __name__ == "__main__":
    assert f(1) == 1
    print("PASS")
