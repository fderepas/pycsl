"""Static gate F2+ — instance-attribute Final: write inside __init__ is OK.

Spec clause F2 (final-twoplane-spec.md §1.2, S5 case (a)): an instance
attribute annotated `attr: Final[T]` declared in class `C`'s body may be
written ONLY inside `C`'s own `__init__` method. The class-body
declaration `attr: Final[int]` (with no `= value`) is NOT a write (F2a —
it establishes the attribute's existence and its `Final` write-policy);
the first (and only) permitted write happens in `__init__`. A reader
method returning `c.attr` discharges normally.

The attribute's type is the inner type `T` (F3 — `Final[int]` → `int`).

Expected (from spec): PASS — the write to `self.attr` inside `C.__init__`
is within the permitted perimeter; the postcondition `\\result == c.attr`
discharges.
"""

from typing import Final


class C:
    attr: Final[int]

    def __init__(self):
        self.attr = 0


#@ ensures \result == c.attr
#@ assigns \nothing
def get(c: C) -> int:
    return c.attr


if __name__ == "__main__":
    obj = C()
    assert get(obj) == 0
    print("PASS")
