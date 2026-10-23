# Route #218 (CLOSED, gen #31) — an explicitly-called DUNDER's self-write is erased, and a `val` with no `writes` is PURE

**Found:** 2026-09-23, gen #30, in the last two hours of the window, by asking lesson
(t3)'s question of one more guard and then checking a claim the corpus already made.

## The decisive signature

```python
#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    #@ ensures self.v == 7
    def __enter__(self) -> int:
        self.v = 7
        return 0


#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _r: int = c.__enter__()
    after: int = c.v
    return before - after
```

    [+] Verification SUCCESS! All contracts formally proven.

CPython answers **-7**. The TRUE twin — the same file with `#@ ensures \result == -7` —
**FAILS**. A false contract proves while the true one is rejected: the route standard,
met exactly.

## The mechanism, and it is a hazard this repo has already written down

The emitted module contains

```
  val c___enter___0 (self: c) : int
```

and nothing else about `__enter__`. It takes the receiver, it returns an `int`, and it has
**no `writes` clause** — because the dunder is not emitted as a `let`, so its
`#@ assigns self.v` never becomes a frame. Why3 reads a `val` with no `writes` as **PURE**,
so `self.v` is provably UNCHANGED across a call that sets it to 7.

`PYCSL-CONTRADICTORY-ASSIGNS` describes this exact failure in its own message:

> SILENTLY PREFERRING EITHER ONE would emit a `val` with no `writes` — which Why3 reads as
> PURE, letting a caller prove the target UNCHANGED across a stub contracted to write it
> (routes #96, #98, #101, #103).

It refuses when a bodyless `val` declares BOTH `assigns \nothing` and a write target. Here
nothing contradicts: the dunder declares one honest `assigns` and the emitter simply drops
it. **The guard's population is stubs whose clauses conflict; this stub's clauses never
reach the emitter at all.** Lesson (t3), for the third time in one night.

## It corrects a claim this campaign made in its own corpus

`1800_gen30_dunder_call_loses_its_contract.py` says:

> SOUND, NOT UNSOUND: a contractless `val` is fresh and unconstrained at every call, so the
> caller can prove LESS, never more.

That is **true about the RESULT and false about the FRAME.** A contractless `val` is fresh
in what it RETURNS, and pure in what it WRITES — and purity is a POSITIVE claim about the
whole heap. The witness's reasoning covered one of the two things a call does. 1800's
docstring now carries the correction and the pointer here.

## Blast radius — and the FIRST TWO MEASUREMENTS OF IT WERE BOTH WRONG

This is worth reading as a worked example of (p3): *print the members before you write a
ceiling.* Three passes were needed.

**Pass 1 (wrong).** "A dunder declaring `#@ assigns self.<f>`" — scanned with an 8-line
window above each `def`, which swallowed the PREVIOUS method's annotations. It reported
three files, including `1334_route120_setattr_hook_dropping_a_store.py`, and that made the
repair look like it would retire route #120's own witness. **False: 1334's `__setattr__`
carries no annotation at all; the `#@ assigns self.a` the window caught belongs to
`__init__`.** Re-done with contiguous-block attribution: **ZERO dunders anywhere declare
`#@ assigns self.`** — corpus, python-reference, mirror, live tree and `pycsl_lib`.

**Pass 2 (right question, wrong key).** So the `#@ assigns` clause is not the trigger at
all. MEASURED: the identical program with the dunder's annotations DELETED still reports
`All contracts formally proven`. **The hole needs only a BODY that writes self state** —
which is why a repair must key on the body, not on a clause.

**Pass 3.** Files with a non-`__init__` dunder whose BODY writes `self.<f>`: **12**, of
which exactly ONE also calls that dunder explicitly — `python-reference/0076.py`
(`# pycsl-expected: FAIL`). The other eleven are route witnesses for #38/#39/#150, `0401`,
`0402` and three library files, none of which call their dunder explicitly.

**And pass 3 nearly went wrong too**, for the reason
`check-refusal-witness-coverage`'s own header warns about: basenames are NOT unique across
corpus directories. The hit printed as `0076.py` is `python-reference/0076.py`;
`pycsl-reference/0076.py` is a different file with no `__setattr__` in it, and it PASSES.
Reporting a basename where two directories can supply it is how a driver ends up checking
the wrong file — twice, in this case, before noticing.

## Two more measurements that narrow it

* **The IMPLICIT dispatch does NOT have the hole.** The same class with `len(c)` instead of
  `c.__len__()` — a `__len__` declaring `#@ assigns self.v` and setting it — **FAILS**. So
  the defect is specific to the EXPLICIT `c.__dunder__(...)` call site, which is exactly
  where the contractless `val` is minted. That makes a repair keyed on the explicit call
  narrower than it first looks.
* **The abstract-op TEMPLATES are clean.** All 96 `_add_abstract_op` `val` templates in
  `module6_whyml/` were scanned: 13 take a non-scalar first parameter and declare no
  `writes`, and every one of those is genuinely READ-ONLY (`join_array`, `sorted_seq`,
  `array_rev`, `array_slice`, `subscript_get_str`, …). The hole is not in the op library;
  it is in the per-call-site `val` minted for a method the emitter DROPPED — and
  `bin/check-emitted-function-coverage.py` says every dropped function in the corpus is a
  dunder, so this route's population and that plane's population are the same set.

## Why it is OPEN and not closed tonight

A refusal keyed on the BODY (pass 3 above) touches exactly one existing file, and deciding
whether refusing it is RIGHT means reading what `python-reference/0076.py` is for — it is a
CPython-reference file about `__getattr__`/`__setattr__`/`__delattr__`, a different
population with different rules from the pycsl-reference corpus. That is a judgement about
another suite's intent, made ninety minutes from a deadline, and it is exactly the kind of
call that should not be made in a hurry: a refusal that quietly retires someone else's
witness is lesson (n3)'s failure, and two of the three measurements above were wrong on the
first try.

**Recording the defect with a blast radius that took three passes to get right is worth
more than a repair nobody checked.**

THREE CANDIDATE REPAIRS, in increasing cost:

1. **Refuse** the explicit call when the target dunder declares `assigns` on self — after
   checking what it does to 1334.
2. **Emit the `writes`**: give the dunder's abstract `val` the frame its `#@ assigns`
   declares. Narrow, and it makes the model HONEST rather than merely silent — the caller
   would then prove nothing about `self.v` instead of proving it unchanged.
3. **Emit dunders** as ordinary methods. The real fix, also what witness 1800 and route
   #216 wait on, and byte-diff-RISKY: authorize-first.

Repair 2 is the one to price first: it is the smallest change that turns a FALSE claim
into an ABSENT one.

## Carrier

`getting-better/open-routes/route218-carrier-dunder-assigns-erased.py` — expects SUCCESS
(the false certificate), registered in `bin/check-open-route-carriers.py`.


---

## CLOSED — 2026-09-23, gen #31, by REPAIR 2 (emit the frame), and the route's own title was wrong

**The title said `#@ assigns`. Pass 2 of the blast radius had already shown the clause is
not the trigger, and the repair proves it: the frame is derived from the DROPPED BODY.**
`Module5._record_skipped_dunder_writes` runs at the `_should_skip_method` early-return and
records, per `<class_lower>__<dunder>`, the self-attribute names the skipped body writes
(plain store, augmented store, annotated store, and element store — the same carve-out
`ir_resolve.self_field_writes` already carries for mixins). `_resolve_dotted_signature`
reads that table when nothing else resolved the callee and builds a `field_spec` whose
writes set is `_writes_filtered_to_labels(cls, recorded)`, so the minted `val` becomes

    val c___enter___0 (self: c) : int
      writes { self.v }

**MAKE-OR-BREAK SPIKE, run before any emitter edit** (`why3 prove -P alt-ergo` on a hand
`.mlw` with that exact `val`): `py_use_false'vc` goes from Valid to **Unknown**. The build
was authorized by that verdict, not by the reading.

**WHAT IT BUYS, STATED HONESTLY: a FALSE claim became an ABSENT one.** The `val` is still
contractless, so the caller now proves nothing about `v` across the call. Measured on the
carrier and its twin: `\result == 0` FAILS (was SUCCESS) and `\result == -7` also FAILS.
Making the TRUE twin prove needs dunders EMITTED as ordinary methods — the larger build
witness 1800 and route #216 still wait on. This repair does not touch it.

**THE NO-INVARIANT TWIN WAS THE MEASUREMENT THE ROUTE DOC DID NOT HAVE.** The recorded
carrier gets its `(self: c)` receiver from route #165 (the class declares invariants). The
same program with the invariant DELETED emitted a receiver-LESS `val c___enter___0 () : int`
and proved just the same — so a repair that only added `writes` to an existing receiver
would have closed one spelling and left the other. Both now carry the receiver and the frame.

**THREE CONTROLS, and each one separates the repair from a different over-broad version:**
* **1816** — a READ-ONLY dunder (`return self.v`) still verifies and its `val` still carries
  no `writes`. The repair is not "a dunder call clobbers the receiver".
* **1817** — the NON-dunder spelling (`def enter`, no annotations) FAILED before and FAILS
  after. That is what pins the defect to `_should_skip_method`, not to the contract, the
  class invariant, or the receiver spelling.
* **1815** — the carrier itself, now an expected-FAIL corpus witness.

Its entry in `bin/check-open-route-carriers.py` is retired in the same commit (the plane's
own message asks for exactly that when a carrier stops proving).


---

## ADDENDUM, SAME DAY — THE REPAIR HAD A HOLE, AND AN INDEPENDENT REVIEWER FOUND IT

`x.__str__()` never reached `_resolve_dotted_signature` at all: `_handle_call_expr`
recognizes it EARLIER and returns the nullary `val str_dunder_op () : string`. So the
identical carrier, with `__enter__` replaced by `__str__`, kept proving the identical false
contract — through the identical mechanism — after this repair landed, was spiked, was
byte-swept over 3509 programs and passed a 45-plane battery.

Recorded as **route #220** (`route220-str-dunder-call-bypasses-the-218-frame.md`), closed
the same day with the same remedy, witnesses 1820/1821.

**Lesson (d4), banked from it:** after landing a repair at a dispatch point, ENUMERATE EVERY
EARLIER RETURN IN THE SAME DISPATCHER. None of this repair's gates could have caught it —
ZERO corpus files call `.__str__()` explicitly, so the byte-diff had nothing to move, and
the recognizer's own comment ("byte-clean") had scoped the EMISSION risk correctly while
saying nothing about the SOUNDNESS risk over the same set.
