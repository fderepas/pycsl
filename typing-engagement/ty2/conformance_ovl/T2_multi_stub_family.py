"""Static gate T2 — multi-stub family, the non-matching stub's guard is vacuous.

Spec clause O3 (§1.1): for each stub carrying `#@ ensures Q_i`, the guarded
postcondition `ensures { G_i -> Q_i }` is attached to the implementation.

Spec clause O6 (§1.2): the implementation body must prove EACH guarded
postcondition `G_i -> Q_i` against its single body. The guards partition the
input space; for each `i`, under `G_i`, the body must establish `Q_i`.

This driver: TWO stubs `f(x: int) -> int` and `f(x: str) -> str`, each with
`#@ ensures \result == x`. The implementation is typed `def f(x: int) -> int: return x`
(TY2 scope restriction §1.6 — the implementation param is annotated so the int
guard decides). The str stub's guarded postcondition `isinstance(x, str) -> \result == x`
is vacuously discharged (the param is `int`, so the str guard is false). The int
stub's is discharged by the body. Call `f(5)` selects the int overload.

Expected (from spec): prove — both guarded postconditions discharge (int
non-vacuously, str vacuously); the call site selects the int overload and proves
`\result == 5`.
"""

from typing import overload


#@ ensures \result == x
@overload
def f(x: int) -> int: ...


#@ ensures \result == x
@overload
def f(x: str) -> str: ...


def f(x: int) -> int:
    return x


#@ ensures \result == 5
def g() -> int:
    return f(5)


if __name__ == "__main__":
    assert g() == 5
    print("PASS")
