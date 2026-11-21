r"""Test 1849 — gen #31 WITNESS: GT1 now fires for the LEGACY `Generic[T]` spelling too.

annotations.md §12.16 lists BOTH spellings in its surface: "`class C[T]: ...`, `def
f[T](): ...`, `T = TypeVar("T", bound=B)` + `class C(Generic[T])`". The static plane is
"Interpreted": whole-module monomorphization, with four loud-fails — GT1 (`Any` never
instantiates a TypeVar, "the consistency relation is deliberately unsound"), GT2 (the
TypeVar bound is an instantiation-time obligation), GT3 (ParamSpec/TypeVarTuple),
GT4 (polymorphic recursion).

For the legacy spelling NONE OF IT RAN. `Module5_IREmitter.visit_ClassDef` attached the
IR's `type_params` only `if getattr(node, "type_params", None)` — the PEP 695 ATTRIBUTE —
so the legacy half of `_collect_type_params` (which resolves the `Generic[T]` base's names
against the `T = TypeVar(...)` registry, with its own `_extract_generic_arg_names` helper)
was DEAD CODE BY CONSTRUCTION: for `class C(Generic[T])` the attribute is `[]`, so the
helper was never called. The monomorphization pass then early-returned, `T` was modelled as
plain `int`, and every one of the four loud-fails was silently inert.

MEASURED, the same program in the two spellings of the same construct:

    class Box[T]          + `b: Box[int]`  ->  type box_int   (monomorphized)
    class Box(Generic[T]) + `b: Box[int]`  ->  type box       (NOT)
    class Box[T]          + `b: Box[Any]`  ->  REFUSED (PYCSL-TY3-GT1)
    class Box(Generic[T]) + `b: Box[Any]`  ->  Verification SUCCESS

This file is the last line of that table and it is `# pycsl-expected: FAIL`. Its twin 1850
is the GT2 half (a bound violated); 1851 is the control that keeps the spelling legal.
"""
# pycsl-expected: FAIL
from typing import Any, Generic, TypeVar

T = TypeVar("T")

_ = 0  # anchor


class Box(Generic[T]):
    def __init__(self, v: T) -> None:
        self.v: T = v

    #@ assigns \nothing
    def get(self) -> T:
        return self.v


#@ ensures \result >= 0
#@ assigns \nothing
def use() -> int:
    b: Box[Any] = Box(0)
    return 0
