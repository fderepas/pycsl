r"""Test 1780 — WITNESS: a generic instantiated with `Any` (GT1).

`PYCSL-TY3-GT1`. `Any` never instantiates a TypeVar: the consistency relation is
DELIBERATELY unsound, so monomorphizing `Box[Any]` would emit a specialized copy whose
field type is the one type that is compatible with everything. Refused
(typing-global-overview.md §5 GT1). One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import Any

_ = 0  # anchor


class Box[T]:
    def __init__(self, v: T) -> None:
        self.v: T = v

    #@ assigns \nothing
    def get(self) -> T:
        return self.v


#@ ensures \result >= 0
def use() -> int:
    b: Box[Any] = Box(0)
    return 0
