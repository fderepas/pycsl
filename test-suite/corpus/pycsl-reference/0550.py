"""Test 0550 — Negative: a `depends_method` with no provider is rejected.

`MapOps` declares a concrete `#@ depends_method emit` (D2) but the composer
`#@ compose_from MapOps` includes NO mixin that `provides emit`. Tier 1's
unique-provider rule (mixin.md S2) requires every dependency to have EXACTLY one
provider; zero providers is a named composition error.

Committed `# pycsl-expected: FAIL` and STAYS failing: today it fails because the
directives don't parse; once Tier 1 lands it must fail for the RIGHT reason — the
unresolved `emit` dependency — not silently verify. Negative companion to the
flagship 0549 (which supplies the provider via `CoreEmit`).
"""
# pycsl-expected: FAIL
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


#@ compose_from MapOps
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
