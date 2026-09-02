"""Test 0968 — a `#@ depends_method` window may declare the dependency's FRAME.

The dependency window already accepted `#@ requires` / `#@ ensures`; without an
`#@ assigns` a declared dependency is FRAMELESS, so the abstract `val` it lowers
to declares no effect at all — and then a provided method that calls it may
declare `#@ assigns \nothing` however much state the real provider writes. That
false frame is invisible to every proof plane, because the model has no effect to
contradict it.

Here `bump` is declared to assign `self.n`. The abstract `val` therefore carries a
`writes` clause, and `handle` — which calls it — MUST declare its own frame. Why3
checks both directions, so this file is an EXECUTABLE WITNESS of exactly the hole
this closes, and both halves were measured:
  * with the window's `#@ assigns self.n` and `handle` weakened to
    `#@ assigns \nothing`, Why3 REJECTS it — "this expression depends on variable
    _pyobj_state, which is left out in the specification" (the coarse cell, since
    `Counter` emits no `n` field label);
  * with the window's `#@ assigns` REMOVED, that same weakened `handle` is
    ACCEPTED — the old, frameless, false-frame behaviour.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class Counter:
    #@ depends_method bump: (self) -> int
    #@   ensures \result >= 0
    #@   assigns self.n
    #@ provides handle
    #@ ensures \result >= 0
    #@ assigns self.n
    def handle(self) -> int:
        return self.bump()

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def n_is(self) -> int:
        return self.n
