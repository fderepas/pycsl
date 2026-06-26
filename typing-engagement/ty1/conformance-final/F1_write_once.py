"""Static gate F1+ — module-level Final is write-once (declaration write).

Spec clause F1 (final-twoplane-spec.md §1.1): a name annotated
`x: Final[T] = v` at module scope may be assigned EXACTLY ONCE: at its
declaration. A function that only READS `x` (no further writes) must
typecheck + prove. The annotation's type is the inner type `T` (F3 —
no narrowing): `Final[int]` has type `int`, so `f -> int` returning
`x` discharges.

Expected (from spec): PASS — the declaration write is at module scope
(not a function body), so the syntactic write-site check does not flag
it; the read of `x` discharges the postcondition.
"""

from typing import Final

x: Final[int] = 5


#@ ensures \result == x
#@ assigns \nothing
def f() -> int:
    return x


if __name__ == "__main__":
    assert f() == 5
    print("PASS")
