r"""Test 1904 — gen #31 CONTROL for 1902 (expected FAIL): inheriting the mixin does NOT
buy an override a free pass.

`Facade` inherits `CoreEmit` *and* defines an `emit` of its own. Python resolves `emit` to
the composer's, so the provider really is shadowed and route #95's refusal is exactly
right — the composer's `emit` never gets checked against the dependency contract that
`MapOps` was verified assuming, and here it plainly violates it (`return -1` under
`ensures \result >= 10`).

1902's exemption cannot fire: it requires the composer's method to BE the provider — same
line, same column, same body, same contracts — and a body the user wrote in the class is
none of those. The base list is not consulted at all, deliberately, because "inherits the
mixin" is not the property that makes shadowing safe; "is the provider" is.

IF THIS FILE EVER PASSES, the exemption has widened from a sameness test to a
base-class test and route #95 is open again for every overriding composer.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ provides emit
    #@ ensures \result >= 10
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return 10


#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 10
    #@ provides handle_get
    #@ ensures \result >= 10
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)


#@ compose_from CoreEmit, MapOps
class Facade(CoreEmit, MapOps):
    #@ ensures \result >= 10
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return -1

    #@ ensures \result >= 10
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
