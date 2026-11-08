r"""Test 1850 — gen #31 WITNESS: GT2 (the TypeVar BOUND) now binds the legacy spelling.

`T = TypeVar("T", bound=Base)` + `class Box(Generic[T])`, instantiated `Box[int]` — and
`int` is not a `Base`. annotations.md §12.16: "The TypeVar bound (`T: B`) is an
instantiation-time obligation (the concrete type must satisfy the bound — invariant
checking, GT2)."

Until gen #31 this VERIFIED, because the legacy spelling never produced IR `type_params`
and the monomorphization pass — which is where GT1/GT2/GT3/GT4 all live — early-returned.
A bound is the one part of a generic's contract a reader is entitled to rely on: a method
verified against `T: Base` may use everything `Base` guarantees, and an instantiation that
does not satisfy the bound hands it a value those guarantees are false of.

Companion to 1849 (GT1, `Any`) and 1851 (the control).
"""
# pycsl-expected: FAIL
from typing import Generic, TypeVar


class Base:
    def __init__(self) -> None:
        self.n: int = 0


T = TypeVar("T", bound=Base)

_ = 0  # anchor


class Box(Generic[T]):
    def __init__(self, v: T) -> None:
        self.v: T = v


#@ ensures \result == 0
#@ assigns \nothing
def use() -> int:
    b: Box[int] = Box(0)
    return 0
