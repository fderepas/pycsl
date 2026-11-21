r"""Test 1908 — gen #31 (expected PASS): a STATEFUL `#@ compose_from` class that also
INHERITS its mixin — `0554`'s shape, made executable.

`1902` did this for the PURE composition. The stateful one needed a second repair, and the
diff between the two emissions of this very program is what found it. `class Service:`
emits

    let service__tick (self: service) : unit = let _ = (service__bump self) in ()

and `class Service(Counter):` emitted, instead, an ABSTRACT operation:

    val self_bump_0 (self: service) : unit
      writes { self.count }                     (* the raw PYTHON field name *)

`_apply_composition`'s flatten loop skips a provider whose tail the composer already has,
and the skip also dropped it from `composed_provider_methods` — the set Module 6 consults
to resolve a composer-OWN `self.<m>(…)` CONCRETELY. Without it the call falls to the
abstract-`val` lowering, which drops `self` and every self-field `ensures`, and the frame
it emits names the field `count` where the record field is `service_count`, so Why3 answers
`unbound function or predicate symbol 'count'`.

`1902` survived that only by accident of WHICH METHOD the call sits in: `Facade.run` calls
`self.handle_get`, and `handle_get` is itself bound from a base, so the inheritance binder
had already rewritten its `self.emit(…)`. `Service.tick` is the composer's own method and
nothing rewrites it. A witness for the pure case was not a witness for this one.

THE REPAIR is the same SAMENESS test one loop over: when the method the composer already
has IS this provider — same line, column, body, contracts — register it as the flattened
provider instead of skipping it, because it is exactly the concrete implementation the
clone would have been.

AND IT RUNS: `Service()` starts at `count = 0`, `tick()` leaves it at 1, which is
`self.count == \old(self.count) + 1`. Before gen #31 no composing class in this corpus
could be executed at all.

WHAT WOULD BREAK IF THIS GOES RED: a composer-own method's call to an inherited provider
has gone back to the abstract-`val` lowering, and with it the self-field postcondition that
makes stateful composition mean anything.

`getting-better/open-routes/finding-a-contract-over-a-function-that-never-returns.md`
"""
# pycsl-expected: PASS
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
class Service(Counter):
    def __init__(self) -> None:
        self.count = 0

    #@ requires self.count >= 0
    #@ ensures self.count == \old(self.count) + 1
    #@ assigns self.count
    def tick(self) -> None:
        self.bump()
