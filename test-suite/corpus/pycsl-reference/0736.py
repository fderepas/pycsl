"""Test 0736 — `Final` instance-attribute witness (F2).

typing-engagement ty1 (27-0000-typing-spec-3): an instance attribute annotated
`attr: Final[T]` in class `C`'s body may be written ONLY inside `C.__init__`
(F2). The class-body `attr: Final[int]` declaration is NOT a write (F2a — it
establishes the attribute's existence and its `Final` write-policy; the first
and only permitted write happens in `__init__). `__init__` is a dunder (skipped
from `ir["functions"]`), so its write to `self.attr` is modelled via the
record's `field_defaults` path, NOT as a function-body statement —
`_check_final` does not flag it. A reader method returning `c.attr` discharges
normally. The attribute's type is the inner type `T` (F3 — `Final[int]` →
`int`).
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
