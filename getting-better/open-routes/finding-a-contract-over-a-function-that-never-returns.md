# A contract over a function that NEVER RETURNS

**Status: FINDING, two instances, both reproduced in CPython and both named in the
instrument.** Not a route: neither certifies a WRONG value, because neither program has a
run in which any value is produced. What they certify is NOTHING — and they certify it
while wearing a contentful postcondition, under `# pycsl-expected: PASS`.

## The shape

    #@ requires k >= 0
    #@ ensures \result == k
    def grab(k: int) -> int: ...

An `#@ ensures` constrains the NORMAL exit. If the function has no normal exit on any
argument its own `#@ requires` admits, the clause is discharged over an empty set of runs.
The prover is right; the proof is empty. This is vacuity — but it is vacuity one level
below where `bin/check-claim-vacuity.py` looks, because that instrument's population is
CLAUSES that are trivially true, and `\result == k` is as contentful as a clause gets.

## Instance 1 — `0496.py::grab`, the `__new__` arity nobody compares

```python
class Holder:
    def __new__(cls):                 # takes NO extra argument
        return super().__new__(cls)
    def __init__(self, n: int):       # takes one
        self.x = n
```

`Holder(k)` is `type.__call__`, which passes the arguments to **both** `__new__` and
`__init__`. With `__new__` overridden at arity 1, CPython raises for every k:

    TypeError: Holder.__new__() takes 1 positional argument but 2 were given

The model never runs `__new__`: it builds the record from `__init__` and discharges
`\result == k`. `__new__` is not an unanalysed surface — **UB-7.6 rejects a NON-TRIVIAL
`__new__`** (caching, singleton, returning another instance), and 0496's own docstring is
about exactly that check: "A trivial `__new__` … is accepted". So the check exists and one
of its dimensions — does the signature admit the construction site's arguments — is
missing. A rule that inspects `__new__` closely enough to classify it as trivial is
standing in front of its arity.

## Instance 2 — `0554.py::Service.tick`, and `#@ compose_from` has no runtime

```python
#@ mixin
class Counter:
    #@ provides bump
    def bump(self) -> None: self.count = self.count + 1

#@ compose_from Counter
class Service:                         # <- does NOT inherit Counter
    def tick(self) -> None: self.bump()
```

`annotations.md` §2.7 says the composer "flattens the providers into the composer so
`self.<m>(…)` resolves end-to-end". It resolves end-to-end IN THE VERIFIER. Python's MRO
is `[Service, object]`, `bump` is not on the instance, and `Service().tick()` is an
`AttributeError` — every time, on the only argument tuple there is.

**Censused across the corpus, because one instance is an anecdote:** thirteen files
mention `compose_from`; eleven declare a composing class; **all eleven compose a provider
they do not inherit**, and in **ten of the eleven** the provided name is absent from the
instance at runtime. The exception is `1259_route95_composer_shadows_depended_provider.py`,
where the composer defines the method itself — which is precisely what that file was
written to witness. Not one composing class in the corpus is executable Python.

The PASS-expected ones are `0549` (the flagship), `0554`, `1261`, `1858`.

`0554`'s docstring calls itself "a faithful miniature of PyCSL's own
facade-with-MUTABLE-shared-state shape (the self-hosting target, `src/self-annotate/`)".
The self-hosting target is a program that runs. The miniature is not.

### Is this a defect or a modelling boundary?

The section HAS a boundary paragraph — "Out of scope (boundaries, documented not faked)" —
and what it scopes out is DYNAMIC dispatch (`getattr(self, _EXPR_DISPATCH[t])`), Tier-2
conflict resolution and Tier-3 diamonds. It does not say the composed program need not run.
Two honest repairs exist and neither is large:

1. **Require the runtime composition.** A `#@ compose_from M` class must have `M` in its
   MRO (or define every provided name itself, which is the `1259` case). This is a
   front-end refusal with a corpus-wide blast radius of eleven files — four of them
   PASS-expected drivers that would need `class Facade(CoreEmit, MapOps)`.
2. **Say so.** Add the sentence to the boundary paragraph, and the corpus stops claiming
   that these files model running code.

Option 1 is the one that makes the directive mean what the documentation says. It is
written down here rather than landed because it is a refusal over a documented directive
with four PASS drivers in its blast radius, and this generation's own lesson (u4) is that
a rule applies to every program that could be written, not just to the ones that exist.

## The instrument

`bin/check-corpus-contract-truth-args.py` grew the bucket that finds these. The tuple loop
used to `break` on the first raise, which cannot tell "raises on THIS argument" (`0420`,
`1302` — input-dependent, already reported under `MAX_RAISED`) from "has no normal exit at
all". It now takes up to three raising tuples per function and classifies afterwards:
a function whose own precondition admitted arguments and which returned on NONE of them is
a `NEVER_RETURNS` entry, and an UNNAMED one turns the plane red. Three entries today:
these two, plus `0159.py::diverges_inc`, which DECLARES `#@ \diverges` and is therefore the
one shape where having no normal exit is the contract rather than a hole in it.

`0554` was invisible to every instrument in the battery until the same commit widened the
oracle to POST-STATE claims (`#@ ensures self.f == \old(self.f) + 1`), because `tick`
returns `None` and has no `\result` clause to read. The widening was aimed at 32 claims it
could newly check; the thing it actually found was a file it could newly RUN.

## Wall-lesson (v5)

**A vacuous proof can wear a contentful clause.** Every vacuity instrument in this repo
looks at the CLAUSE — is it `True`, is it `x == x`, does it constrain anything. None looked
at whether the function has a normal exit for the clause to constrain. The second question
is cheaper to ask than the first and had never been asked.

---

## ADDENDUM — the proposed repair was MEASURED, and PyCSL REFUSES it

Option 1 above says "require the runtime composition": a `#@ compose_from M` class must
have `M` in its MRO. Before writing that down as the recommended repair it was tried, on
offline copies of the two PASS-expected drivers, with a one-token edit each:

    class Facade:                ->  class Facade(CoreEmit, MapOps):
    class Service:               ->  class Service(Counter):

**Both now RUN, and both produce the values their contracts claim.** `Facade().run(3)` is
`3`, `Facade().run(-1)` is `0` — both `>= 0`, which is `run`'s postcondition. `Service()`
starts at `count = 0` and `tick()` leaves it at `1`, which is
`self.count == \old(self.count) + 1`. The inheritance is not a workaround; it is the
composition the directive describes, spelled the way Python spells it.

**And PyCSL refuses the first one and fails the second.**

### `0549` inheriting its mixins — REFUSED by route #95's shadow check

    Mixin composition 'Facade': 'Facade' defines its own 'emit', which SHADOWS the
    provider of 'emit' (from mixin CoreEmit) that mixin MapOps declares a
    `#@ depends_method` on. […] Rename 'Facade.emit', or drop the dependency declaration.

`Facade` defines `run`. That is the whole class body — `emit` arrives by inheritance from
`CoreEmit`, **the very mixin the composition names as its provider**. The check
(`src/pycsl/frontend/ir_resolve.py` ~2803) computes

    own_tails = {f["name"][len(c) + 2:] for f in funcs if f["name"].startswith(c + "__")}

from the IR function list, and the base-class binding machinery (routes #144/#147) has
already materialised `Facade__emit` there. So an INHERITED method is indistinguishable
from a DEFINED one at that line, and the diagnostic's first clause — "'Facade' defines its
own 'emit'" — is simply false of the program in front of it.

The check's own comment is careful and correct about the danger it guards: a composer that
defines a DIFFERENT, weaker `emit` deletes the S2b re-verification while `MapOps` is
verified assuming it holds, and it names the measured witness (`provides emit ensures
\result == 0` under `depends_method emit ensures \result >= 10`). That danger is real. It
is also **absent by construction** in the inherited case: the shadowing method IS the
provider, the same function object, the same contract. There is no unverified substitution
because there is no substitution.

So the state of affairs is:

* write the composition the way the documentation's example writes it — the class runs
  nothing, and PyCSL verifies it;
* write the composition the way Python composes — the class runs correctly, and PyCSL
  refuses it as a shadow.

**The directive that exists to make mixin composition machine-checkable refuses the only
Python construct that performs it.**

### `0554` inheriting its mixin — a lowering failure, not a refusal

    unbound function or predicate symbol 'count'   (line 15 of the emitted .mlw)

A different mechanism and a different level: this one gets past the front end and dies in
the generated WhyML, where the stateful mixin's `count` field does not resolve once
`Counter` is also a real base. Recorded as measured; not diagnosed further here.

### What this does to the repair

Option 1 is **not** a small front-end refusal with an eleven-file blast radius. It is a
three-part change — teach route #95's `own_tails` to exempt a provider inherited from the
providing mixin itself, fix the stateful-composition lowering under a real base, and only
THEN require the MRO edge — and each part has to be measured on its own. That is written
down rather than landed because it is a design change to a documented directive, and this
generation's lesson (u4) applies: a rule binds every program that could be written, not
only the eleven that exist.

What is cheap and unambiguous is the FIRST part alone, independent of any new rule: a
composer that inherits the providing mixin is not shadowing anything, and telling it that
it "defines its own" method is a false diagnostic on a correct program.

---

## ADDENDUM 2 — the stateful half, diagnosed by DIFFING two emissions

The first exemption made the PURE composition (`0549`'s shape) both run and verify. The
STATEFUL one (`0554`'s) still died in the emitted WhyML:

    unbound function or predicate symbol 'count'

Emitting both spellings of the same file with `--no-proof --no-typecheck --keep-mlw` and
diffing them isolates it to one line. `class Service:` emits

    let service__tick (self: service) : unit
      ensures { self.service_count = old self.service_count + 1 }
    = let _ = (service__bump self) in ()

and `class Service(Counter):` emits, instead,

    val self_bump_0 (self: service) : unit
      writes { self.count }                      (* <- line 15, characters 18-23 *)
      ensures { self.service_count = old self.service_count + 1 }
    ...
    = let _ = begin assert { ... }; (self_bump_0 self) end in ()

Two things, in order:

1. **The concrete invocation was lost.** `_apply_composition`'s flatten loop skips a
   provider whose tail the composer already has (`if tail in own_tails … continue`), and
   the skip ALSO drops it from `composed_provider_methods` — the set Module 6 consults
   (`module6_whyml/expressions.py` ~6956) to resolve a composer-own `self.<m>(…)` to the
   CONCRETE `<composer>__<m>`. Without it the call falls to the abstract-`val` lowering,
   "which drops `self` and self-field ensures" in that code's own words.

   Why the pure case survived: `Facade.run` calls `self.handle_get`, and `handle_get` is
   itself a method BOUND FROM A BASE, so the inheritance binder had already rewritten its
   `self.emit(…)` to `facade__emit`. `Service.tick` is the composer's OWN method, written
   in `Service`, and nothing rewrites it. The pure case worked by accident of which method
   the call sits in.

2. **The abstract-`val` fallback emits the RAW PYTHON FIELD NAME in its frame.**
   `writes { self.count }` where the record field is `service_count`.

   **CORRECTION, measured after that sentence was first written as "a path no corpus file
   reached".** It is reachable TODAY, with no inheritance and none of this generation's
   changes: take `0554` exactly as the corpus has it and give `Service` its own `bump`.
   `own_tails` then holds `bump`, the clone is skipped, `self.bump()` in `tick` falls to
   the abstract `val`, and the LIVE tree answers

       unbound function or predicate symbol 'count'

   So the defect is not an artefact of making the composition executable — making it
   executable is simply the second way to walk a path that was already open. The rule that
   caught this is the one this campaign keeps re-learning: **before writing "no program
   reaches this", write the program.**

   `src/pycsl/module6_whyml/expressions.py` ~7396 builds the clause as

       _wparts = [f"self.{f}" for f in writes_fields]

   from the RAW `#@ assigns` target, while `_writes_filtered_to_labels` immediately above
   it maps each target through `self._field_label(cls, f)` — but only to TEST membership,
   never to emit. One line maps and discards; the next line emits unmapped. The failure is
   fail-closed (Why3 refuses the symbol, the file FAILS), so it costs a DIAGNOSIS rather
   than soundness — the same shape as the undeclared-element-write finding in gen #30.
   Recorded here with its measurement; the repair is a separate increment with its own
   byte-diff, because `_field_label` is a rename that every caller-side frame in the corpus
   would flow through.

**The repair** is the same sameness test, applied at the flatten loop instead of the
shadow check: when the method the composer "already has" IS this provider — same line,
column, body, contracts — register it in `composed_provider_methods` rather than skipping
it silently. It is the concrete implementation the clone would have been.

Measured: `0554` made executable now verifies, `0554` as written still verifies, `0549`
both ways verifies, and all thirteen mixin drivers in the corpus keep their verdicts. The
adversarial `1903` still FAILS.
