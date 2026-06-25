"""Static gate C9 (positive) — match exhaustiveness, all arms covered.

Spec clause C9 (union-twoplane-spec.md §1.3): a `match` on a value of type
`Union[A_1, ..., A_n]` must cover every arm. This driver covers both arms
of `Union[int, str]`.

Expected (from spec): prove (exhaustive match over all constructors).
"""

from typing import Union


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def f(x: Union[int, str]) -> int:
    match x:
        case int():
            return 1
        case str():
            return 2


if __name__ == "__main__":
    assert f(1) == 1
    assert f("a") == 2
    print("PASS")
