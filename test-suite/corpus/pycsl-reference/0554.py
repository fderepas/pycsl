"""Test 0554 — Gate-A demand-driver: STATEFUL mixin composition (Tier-1 follow-on).

A faithful miniature of PyCSL's own facade-with-MUTABLE-shared-state shape (the
self-hosting target, `src/self-annotate/`). Unlike the pure-method flagship 0549
(whose mixins `assigns \nothing` and only compute), here a mixin method MUTATES
the shared facade state through the composed record — a real state transition:

  - `Counter` is a `#@ mixin` that `provides bump`, declares the shared facade
    field `count`, and writes it (`self.count = self.count + 1`);
  - `Service` `#@ compose_from Counter`, owns `count` via `__init__`, carries a
    `#@ class invariant self.count >= 0`, and calls `self.bump()` in `tick`,
    expecting the post-state `self.count == \\old(self.count) + 1` to flow through
    the composition to `tick`'s own postcondition.

NOT a stays-FAIL negative (cf. 0550/0551/0552, which assert composition *errors*).
This is a FAIL-until-BUILT Gate-A driver, like 0549 was before S2: it fails today
only because Tier-1-as-shipped does not yet support *stateful* composition, and it
must FLIP to PASS when that lands.

WHY IT FAILS TODAY (the demand). Two concrete gaps, both rooted in the verify-once
abstract-`val` model that suffices for pure methods but not for state:
  (1) a `#@ shared_state` mixin with no own `__init__` emits as an opaque
      `type counter = int` (not a record), so the cloned `counter__bump`'s
      `self.count` mis-types against an `int`-typed `self`;
  (2) the abstract `val` synthesized for a provided method drops `self` and any
      self-field-referencing `ensures` (the standing method-call-contract gap),
      so `self.bump()`'s post-state `self.count == \\old(self.count) + 1` never
      reaches `Service.tick` — the mutation is invisible to the composer, and
      `tick`'s postcondition cannot be discharged.

WHAT FLIPS IT TO PASS (the spec for the follow-on):
  - a stateful `#@ mixin` emits as a WhyML record carrying its shared/owned fields;
  - on `compose_from`, a provided method composes as a CONCRETE `<composer>__m self`
    call (not an abstract `val`), so the shared-field post-state propagates;
  - the composed record conjoins each mixin's `#@ class invariant` over the shared
    field, and a write to shared state appears in the method's `assigns` (existing
    check) — recovering soundness the PyCSL way (mixin.md D1).

Contrast 0549 (pure methods) — there the abstract-`val` model is sufficient
*because* nothing mutates shared state; that is exactly the boundary this driver
pushes past.
"""
# pycsl-expected: FAIL
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


#@ compose_from Counter
class Service:
    #@ class invariant self.count >= 0

    def __init__(self) -> None:
        self.count = 0

    #@ requires self.count >= 0
    #@ ensures self.count == \old(self.count) + 1
    #@ assigns self.count
    def tick(self) -> None:
        self.bump()
