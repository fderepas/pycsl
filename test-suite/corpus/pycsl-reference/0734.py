"""Test 0734 — `Final[int]` module-level witness (F1).

typing-engagement ty1 (27-0000-typing-spec-3): `Final[T]` at module scope is a
write-restriction — write-once at the declaration (F1). The declaration
`x: Final[int] = 5` is the single permitted write (it lives at module scope,
NOT in a function body, so `_check_final` does not flag it). A function that
reads `x` (a read, not a write) discharges normally. The annotation's type is
the inner type `T` (F3 — no narrowing): `Final[int]` has type `int`.
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
