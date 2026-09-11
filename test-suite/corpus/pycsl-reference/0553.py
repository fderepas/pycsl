"""Test 0553 — S1 verify-once: a mixin proves against its abstract dependency.

A single `#@ mixin` verified IN ISOLATION (no `#@ compose_from`). `MapOps`
declares a concrete `#@ depends_method emit: (self, x: int) -> int` with the
dependency contract `ensures \result >= 0`, and `provides handle_get`. The
provided method calls `self.emit(k)`.

PyCSL emits the declared dependency as an abstract `val emit (x: int) : int
ensures { result >= 0 }` (the abstract-op / val-bridge pattern) and verifies
`handle_get`'s own postcondition `\result >= 0` against it — `self.emit(k) >= 0`
discharges it. This is the S1 milestone: a mixin's provided method proves
against its abstract `depends_method` interface, BEFORE any composition supplies
a concrete provider (that refinement is S2, exercised by the flagship 0549).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)
