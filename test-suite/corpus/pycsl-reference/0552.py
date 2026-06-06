"""Test 0552 — Negative: a silent method collision is rejected.

Both `CoreEmit` and `AltEmit` `#@ provides emit`, and the composer
`#@ compose_from CoreEmit, AltEmit` does NOT resolve the clash. Tier 1's
unique-provider rule requires EXACTLY one provider per method name; two providers
of `emit` with no `#@ resolve`/`#@ exclude` (Tier 2) is a named composition
error — never a silent last-writer-wins.

Committed `# pycsl-expected: FAIL` and STAYS failing: today the directives don't
parse; once Tier 1 lands it must fail for the RIGHT reason — the unresolved
two-provider collision on `emit` — not silently pick one. Resolving it is Tier 2
(`#@ resolve emit from CoreEmit`), gated on a real conflict, so this driver also
documents the Tier-1/Tier-2 boundary.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0


#@ mixin
class AltEmit:
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x + 1 if x >= 0 else 1


#@ compose_from CoreEmit, AltEmit
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.emit(k)
