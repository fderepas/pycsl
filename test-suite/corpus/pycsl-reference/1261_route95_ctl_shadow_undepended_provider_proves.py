"""Test 1261 — route #95 CONTROL (NARROWNESS): shadowing a provider that NOTHING declares a
`#@ depends_method` on is still allowed, and still proves.

`Facade` defines its own `handle_get`, shadowing `MapOps`'s provider. No mixin declares a
dependency on `handle_get`, so no dependency contract is being ASSUMED anywhere on its behalf
— the composer simply owns the method, and `self.handle_get(k)` in `run` resolves to
`Facade`'s own concrete implementation. There is nothing for S2b to be about.

This is the rule-(l) negative test for route #95's repair, kept as a standing witness: the
repair rejects `shadow ∧ depended-on`, not `shadow`. A future widening of the check to all
shadowed providers would turn this file red, which is the point of keeping it.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return 0


#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)


#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:    # shadows a provider nothing DEPENDS on
        return 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
