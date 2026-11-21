# FINDING (w56) — a frameless `#@ depends_method` window is FAIL-OPEN, and only a type accident hides it

**STATUS: CONFIRMED LIVE, but NOT a demonstrated soundness route.** Recorded with the exact
step that is missing, so the next generation neither re-probes it nor overclaims it.

## WHAT IS ESTABLISHED, BY MEASUREMENT

Driver `0968_requires_method_frame.py` documents this hole in its own docstring. I ran the
experiment that docstring describes, on 0968's known-good shape, and **both halves reproduce**:

| variant | result |
|---|---|
| 0968 as committed (window declares `#@ assigns self.n`) | PROVES (baseline) |
| window frame KEPT, `handle` weakened to `#@ assigns \nothing` | **FAILS** — Why3 rejects |
| window frame REMOVED, `handle` weakened to `#@ assigns \nothing` | **PROVES** |

So the frame is genuinely checked *when declared*, and **omitting `#@ assigns` from a
dependency window is FAIL-OPEN**: the dependency lowers to an abstract `val` declaring no
effect, and a method that calls it may then claim `assigns \nothing` no matter what the real
provider writes.

**The 2026 fix made the frame DECLARABLE, not REQUIRED.** That is the whole finding.

## WHAT IS *NOT* ESTABLISHED — AND WHY I AM NOT CALLING IT A ROUTE

No false VALUE claim about a running program has been demonstrated, because **a composed
mixin whose provider actually WRITES a field does not emit at all.** Four spellings, four
non-results (an emission failure is not a semantic result):

* `#@ shared_state n: int` + `assigns self.n` → `unbound function or predicate symbol 'n'`
* no field declaration → refused: "a method writes `self.n`, a field declared neither
  `#@ shared_state` nor `#@ touches_field` nor initialised in `__init__`"
* `#@ touches_field n: int` → ill-typed: "This expression has type int, but is expected to
  have type PyCSL_Program"
* `#@ shared_state n: int` (composed) → the same ill-typed emission

**No driver in the tree has a mixin that concretely writes a field AND is composed** — 0968's
`bump` is an abstract dependency and its `handle` writes nothing; 0549/0550/0553 are all
read-only `emit` helpers.

**So the false frame is currently harmless BY TYPE ACCIDENT, NOT BY A GUARD** — the exact
distinction this campaign keeps having to redraw (cf. gen #5's object-typed locals).

## REOPENING CONDITION — sharp, and worth watching

**The day a composed mixin can have a provider that writes a field, the frameless dependency
window becomes a live soundness route.** That is not speculative: the acceptance half is
already measured (row 3 above); only the emission half is missing.

## THE REPAIR, SCOPED AND CENSUSED

**REQUIRE `#@ assigns` in every `depends_method` / `requires_method` window; refuse
otherwise**, naming what could not be shown. Fail-closed by construction, and it matches the
campaign's house style (refuse the claim, do not guess it).

Rejected alternative: defaulting a frameless dependency to "writes everything". That forces
every caller to widen its frame and would break far more than it fixes.

**BLAST RADIUS CENSUSED: FIVE real directive sites**, and every one is an effect-free helper
that can honestly declare `#@   assigns \nothing`:
`0549`, `0550`, `0553` (`depends_method emit`), plus the mirror's `requires_method
_field_type_of` and `_seq_operand`.

## THE REPAIR WAS BUILT, GATED, AND THEN REVERTED — AND THE REASON IS THE USEFUL PART

**The estimated cost was wrong in BOTH directions, and only measurement found either.**

*Cheaper than estimated:* I had recorded this as owing a whole-file mirror re-proof. In fact
`_extract_mixin_directives` is a **`\trusted` STUB in the mirror** (body `return []`) — the
cheap side — and the mirror's emission with the frame added is **BYTE-IDENTICAL** (293231
bytes). No re-proof was owed at all.

*More expensive than estimated:* the built repair passed **everything**: 33 planes green,
**both** corpora fully byte-inert (969/969 and 2204/2204, 0 moved / 0 gone / 0 appeared),
all four mixin drivers correct. Then `run-reference-tests.sh` aborted at its **leading gate**:

    IR CONFORMANCE FAILED — 0549 MISMATCH, 0553 MISMATCH

Those two drivers carry **FROZEN IR GOLDENS** in `test-suite/corpus/conformance/`, and the
`#@   assigns \nothing` the repair forces into their dependency windows changes the derived
IR.

**THE LESSON: A GREEN BYTE-DIFF DOES NOT COVER THE IR.** Byte-inertness is about emitted
WhyML; the conformance gate is about the IR one stage earlier. A landing can be perfectly
byte-inert on both corpora and still break a frozen contract.

**WHY REVERTED RATHER THAN REFRESHED.** The tool's own message requires an
`IR_VERSION`/`ACCEPTED_IR_VERSIONS` bump plus refreshed goldens for a deliberate change, and
"refresh the baseline until the gate is green" is precisely the banked lesson *never
re-baseline a ratchet to make it green*. Decisively, **this hole is not currently
exploitable** (a composed mixin with a writing provider does not emit), so this is DEFENSIVE
HARDENING — which does not justify unilaterally editing a frozen contract.

**TRUE COST, NOW MEASURED:** landing this requires refreshing the IR goldens of 0549 and 0553
(and the version-bump question that raises). That is a decision about a frozen contract, not
a worker's unilateral call. The build itself is straightforward and is described above.

---

## UPDATE (#49, gen #31, 2026-09-23) — the emission blocker is GONE, and the route still does not land

The four "non-results" above all failed to EMIT. Three of them share one cause and it is now
known: **a composed mixin that concretely writes a field emits fine, provided the COMPOSER
initialises that field in its own `__init__`.** The composer's record is built from the
composer's `__init__`, not from the mixins' `#@ shared_state`/`#@ touches_field` lines, so a
clone that writes `self.cache` into a fieldless `type facade = int` is what produced
`This expression has type int, but is expected to have type PyCSL_Program`. Add
`def __init__(self) -> None: self.cache: int = 0` to the composer and the same file verifies.
(That shape is now the `shared_state`/`touches_field` pair in
`bin/check-directive-enforcement.py`, so it stays built.)

So the experiment this finding could not run in its generation was run in this one:

```python
#@ mixin
class CoreBump:
    #@ touches_field n: int
    #@ provides bump
    #@ ensures \result == 0
    #@ assigns self.n                 # the provider WRITES
    def bump(self) -> int:
        self.n = 5
        return 0

#@ mixin
class Handler:
    #@ depends_method bump: (self) -> int
    #@   ensures \result == 0        # NO `#@ assigns` in the window — the fail-open shape
    #@ provides handle
    #@ ensures \result == 0
    #@ assigns \nothing              # the LIE
    def handle(self) -> int:
        return self.bump()

#@ compose_from CoreBump, Handler
class Facade:
    def __init__(self) -> None:
        self.n: int = 0
    #@ ensures self.n == 0           # false of the real program
    #@ assigns \nothing
    def run(self) -> int:
        return self.handle()
```

**FAILS.** Reading the emitted WhyML pins exactly where, and it is the good place:

```whyml
  let handler__handle (self: handler) : int          (* isolated: type handler = int *)
    ensures  { (result = 0) }                        (* <-- NO FRAME. fail-open, as w56 says *)
  let facade__handle (self: facade) : int            (* the CLONE *)
    ensures  { (result = 0) }
    ensures  { self.facade_n = old self.facade_n }   (* <-- the frame, against the real write *)
```

The isolated mixin proof IS frameless, confirming w56's core claim unchanged; the **clone** is
where `assigns \nothing` becomes a real obligation, and it is unprovable because
`facade__bump` writes `facade_n`. This is the S2b compensation (route #95 / finding w66)
doing its job on the FRAME as well as on the VALUE contract — which was not previously
measured.

**Net: w56 stays CONFIRMED and stays NOT-A-ROUTE, but the reason is now positive rather than
an emission failure.** The remaining exposure is unchanged and worth restating precisely: the
frameless window is only compensated for what FLATTENING re-verifies. A mixin verified and
shipped WITHOUT being composed (or any future change that makes flattening lazier) keeps a
`let` whose `assigns \nothing` was never checked against a writing provider.
