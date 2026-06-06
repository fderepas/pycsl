"""Test 0554 — STATEFUL mixin composition (Tier-1 stateful extension).

A faithful miniature of PyCSL's own facade-with-MUTABLE-shared-state shape (the
self-hosting target, `src/self-annotate/`). Unlike the pure-method flagship 0549
(whose mixins `assigns \nothing` and only compute), here a mixin method MUTATES
the shared facade state through the composed record — a real state transition:

  - `Counter` is a `#@ mixin` that `provides bump`, declares the shared facade
    field `count`, and WRITES it (`self.count = self.count + 1`);
  - `Service` `#@ compose_from Counter`, owns `count` via `__init__`, carries a
    `#@ class invariant self.count >= 0`, and calls `self.bump()` in `tick`,
    where the post-state `self.count == \\old(self.count) + 1` flows through the
    composition to `tick`'s own postcondition.

PASSES under stateful composition (the extension that flipped this from FAIL).
Three mechanisms make the mutation provable end-to-end:
  (1) a stateful `#@ mixin` (one whose methods declare `#@ shared_state` /
      `#@ touches_field`) emits as a WhyML RECORD carrying those fields — so the
      cloned `counter__bump`'s `self.count` type-checks (was `type counter = int`);
  (2) on `compose_from`, a provided method is invoked CONCRETELY —
      `(service__bump self)`, not an abstract `val` — so the provider's full
      state-mutating contract (`assigns self.count`,
      `ensures self.count == \\old(self.count) + 1`) reaches `tick`. This closes,
      for the composed case, the method-call-contract gap that drops `self` and
      self-field `ensures` from the abstract-`val` lowering;
  (3) the composed record conjoins the class invariant `self.count >= 0`, which
      Why3 then checks every mutating method maintains.

Contrast 0549 (pure methods) — there the abstract-`val` model is sufficient
*because* nothing mutates shared state; this driver is the same algebra pushed
past that boundary into mutable shared state.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class Counter:
    #@ shared_state count: int
    #@ provides bump
    #@ requires self.count >= 0
    #@ ensures self.count == \old(self.count) + 1
    #@ assigns self.count
    def bump(self) -> None:
        self.count = self.count + 1


#@ class invariant self.count >= 0
#@ compose_from Counter
class Service:
    def __init__(self) -> None:
        self.count = 0

    #@ requires self.count >= 0
    #@ ensures self.count == \old(self.count) + 1
    #@ assigns self.count
    def tick(self) -> None:
        self.bump()
