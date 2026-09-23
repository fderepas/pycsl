r"""Test 1851 — gen #31 CONTROL for 1849/1850 (expected PASS): the spelling stays legal.

A `class Box(Generic[T])` that is never INSTANTIATED. annotations.md §12.16: "An
un-instantiated generic emits NO specialized copy and is recorded Ignored/GT8." It
verifies, so the refusals in 1849 and 1850 are about the INSTANTIATION — `Any`, and a
concrete type outside the declared bound — and not a ban on the legacy `Generic[T]`
spelling itself.

Without this control the two witnesses could not distinguish "the documented rules now
apply to both spellings" from "the legacy spelling was outlawed", and the second would be
a regression dressed as a repair.
"""
# pycsl-expected: PASS
from typing import Generic, TypeVar

T = TypeVar("T")

_ = 0  # anchor


class Box(Generic[T]):
    def __init__(self, v: T) -> None:
        self.v: T = v

    #@ ensures \result == self.v
    #@ assigns \nothing
    def get(self) -> T:
        return self.v


#@ ensures \result == 3
#@ assigns \nothing
def use() -> int:
    return 3
