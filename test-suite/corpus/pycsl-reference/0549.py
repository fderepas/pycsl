"""Test 0549 — Flagship: disciplined mixin composition (Tier 1).

The Gate-A demand-driver for `mixin.md` / `mixin-ready.md`. A faithful *miniature*
of PyCSL's own facade-with-shared-state mixin shape (the self-hosting target,
`src/self-annotate/`), not a textbook toy:

  - `CoreEmit` is a `#@ mixin` that `provides emit` and declares the shared facade
    state `program_ir` (D1 — deliberately shared, not an owned-field conflict);
  - `MapOps` is a sibling handler `#@ mixin` that `provides handle_get` and has a
    CONCRETE `depends_method` on the sibling `emit` (D2 — a real cross-mixin
    dependency, not an abstract hole), calling `self.emit(k)`;
  - `Facade` `#@ compose_from CoreEmit, MapOps` and calls `self.handle_get`.

FAILS today only because mixin composition is unexpressible (the `#@ mixin` /
`#@ provides` / `#@ depends_method` / `#@ compose_from` directives do not parse).
Flips to PASS when Tier 1 lands (S2 composition check): the unique provider for
`emit` is found, its contract refines the declared dependency, and the flattened
`Facade` proves `run`'s postcondition end-to-end.

HONEST CAVEAT (links mixin-ready.md R2/R4): this is a faithful-but-idealised
miniature — it uses STATIC `provides`/`depends_method`, not the real facade's
`getattr(self, _EXPR_DISPATCH[t])` dict-keyed dynamic dispatch (probed
2026-06-06, scoped out of Tier 1). Passing it proves the mixin *algebra* works,
not that PyCSL's real facade is fully self-verifying (that needs Tier 1.5).
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
        return x if x >= 0 else 0


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
    def run(self, k: int) -> int:
        return self.handle_get(k)
