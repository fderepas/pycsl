"""Static gate C9 (negative) — match non-exhaustiveness must FAIL.

Spec clause C9 (union-twoplane-spec.md §1.3): a `match` on a value of type
`Union[A_1, ..., A_n]` must cover every arm. This driver covers only the
`int` arm of `Union[int, str]` — the `str` arm is uncovered.

Expected (from spec): FAIL (non-exhaustive match is a static error).
"""

from typing import Union


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def f(x: Union[int, str]) -> int:
    match x:
        case int():
            return 1


if __name__ == "__main__":
    assert f(1) == 1
    print("PASS")
