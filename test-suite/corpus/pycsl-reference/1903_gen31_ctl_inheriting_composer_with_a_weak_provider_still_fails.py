r"""Test 1903 — gen #31 CONTROL for 1902 (expected FAIL): the composer inherits its mixins
AND the provider does not refine the declared dependency.

THE QUESTION THE EXEMPTION HAS TO ANSWER. Route #95 is a severity-1 route: skipping the
clone of a shadowed provider removes it from the re-verified population, so a sibling
mixin's method keeps resolving `self.emit(…)` to an abstract `val` carrying the DECLARED
DEPENDENCY's contract while a weaker implementation is what actually runs. 1902's exemption
skips the shadow REFUSAL. Does it also skip the check?

It does not, and this file is the proof. `CoreEmit provides emit ensures \result == 0`;
`MapOps depends_method emit ensures \result >= 10`. The inherited `facade__emit` is a real
function of the composer carrying the PROVIDER's contract, and it is verified against the
composer exactly as a clone would be — so `run`'s `\result >= 10` is unprovable and the
file FAILS, which is the same verdict the plain (non-inheriting) spelling of this program
already gets.

This file is the (u4) counter-program, constructed BEFORE the exemption was landed rather
than after it: the strongest program the new rule would ADMIT, checked to see whether
admitting it costs anything.

IF THIS FILE EVER PASSES, the exemption has reopened route #95 through inheritance and must
be withdrawn.
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
class Facade(CoreEmit, MapOps):
    #@ ensures \result >= 10
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
