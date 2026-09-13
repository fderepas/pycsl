"""Test 1260 — route #95 CONTROL: the SAME weak provider, with NO composer shadow, FAILS.

Identical to 1259 except that `Facade` does not define its own `emit`. `CoreEmit.emit` is then
flattened into `Facade` and RE-VERIFIED there, so `facade__handle_get`'s postcondition
(`\result >= 10`) is checked against the concrete `\result == 0` provider and cannot be
discharged (the unproven goal is `facade__handle_get'vc`). This is finding w66's measurement,
re-stated as a standing control.

ITS JOB IS TO PIN THE DIFFERENTIAL: 1259 and this file differ by exactly one method, and that
method flips FAIL to SUCCESS. Without this control, 1259's repair could be mistaken for a
general rejection of weak providers; with it, the repair is pinned to the SHADOWING.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ provides emit
    #@ ensures \result == 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return 0


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
class Facade:
    #@ ensures \result >= 10
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
