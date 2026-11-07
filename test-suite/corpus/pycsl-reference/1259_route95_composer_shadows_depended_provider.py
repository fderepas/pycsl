"""Test 1259 — route #95, NEGATIVE: a composer method that SHADOWS a depended-on mixin
provider deletes the only thing that was ever checking `provider ⊑ dependency` (S2b).

`ir_resolve.apply_composition` never implements S2b — `grep -rn S2b src/pycsl/` returns one
line, the comment deferring to it. Finding w66 certified that as COVERED, because the pass
deep-copies each provider into the composer and the clone is RE-VERIFIED against the concrete
provider; a provider that fails to refine its declared dependency makes the composed file fail.
That is true — on the population it flattens.

The flatten loop skips a provider whose tail the composer already defines:

    if tail in own_tails or new_name in existing:
        continue   # composer overrides it, or already cloned

For DISPATCH that is correct override semantics. What it also does is remove the method from
the re-verified population and from `composed_provider_methods`, so the sibling's clone keeps
resolving `self.emit(k)` to an abstract `val` carrying the DECLARED DEPENDENCY's contract
(`\result >= 10`) while `Facade.emit` — which returns 0 and was never verified against
anything — is what actually runs.

MEASURED BEFORE THE REPAIR: this file VERIFIED, proving `run() >= 10`. CPython on the same
shape with the mixins as real bases returns **0**. Controls: 0549 PROVES (the algebra is
alive), 1260 is this file with `Facade.emit` DELETED and it FAILS — so the shadowing method
is exactly what deletes the check — and 1261 shadows a provider nothing DEPENDS on and still
proves, so the repair is narrow.

>>> A COMPENSATING MECHANISM THAT IS NOT A CHECK HAS NO OBLIGATION TO BE TOTAL, AND WILL NOT
>>> BE. When a missing check is certified as "covered by another mechanism", the question is
>>> not "does it cover this case" but "what is its population, and who keeps it equal?"
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
    #@ ensures \result == 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:      # SHADOWS CoreEmit's provider — never re-verified
        return 0

    #@ ensures \result >= 10
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
