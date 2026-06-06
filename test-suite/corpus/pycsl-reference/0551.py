"""Test 0551 — Negative: writing an undeclared field is rejected.

`CoreEmit.emit` writes `self.cache` — a field that is declared neither
`#@ shared_state` (deliberately-shared facade state, D1) nor `#@ touches_field`
(an owned field). Tier 1 classifies every field a mixin touches; a write to an
UNDECLARED field is a named composition error (you cannot reason about facade
state a mixin never declared it touches, and the write would also be missing from
`assigns`).

Committed `# pycsl-expected: FAIL` and STAYS failing: today the directives don't
parse; once Tier 1 lands it must fail for the RIGHT reason — the undeclared
`self.cache` write — not silently verify. Contrast the flagship 0549, where
`program_ir` IS declared `#@ shared_state`.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        self.cache = x        # cache is neither shared_state nor touches_field
        return x if x >= 0 else 0


#@ compose_from CoreEmit
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.emit(k)
