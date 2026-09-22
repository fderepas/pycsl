# Routes #213 and #214 — the two `getattr` devices, read as the claims they are

Both came out of ONE sentence that route #197 wrote about its own repair:

> hashed on the call's IR so two reads of the SAME `getattr` expression agree (which
> `(any int)` would NOT give — it is fresh at every evaluation, and losing that equality is
> a real loss of faithfulness for no gain)

That equality is a CLAIM. It is sound exactly while the thing being read cannot change
between the reads, and while the two reads really are reads of the same thing.

## Route #213 — **OPEN** (the refusal was landed and then reverted). Two reads of the same `getattr`, across a call that writes it

```python
#@ assigns o.a
def mutate(o: Any) -> None:
    o.a = 99

#@ assigns o.a
#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a")
    mutate(o)
    y = getattr(o, "a")
    return x - y
```

**PROVED.** CPython answers **-98** for an object whose `a` is 1. The emission says why:

```whyml
val function pycsl_getattr_missing_1929893044 : int          (* a CONSTANT *)
val setattr_3 (x: int) (f: int) (v: int) : unit writes { _pyobj_state }
x := pycsl_getattr_missing_1929893044;
(mutate o);
y := pycsl_getattr_missing_1929893044;
```

The device does not depend on the state it is supposed to read.

**Two earlier variants FAILED for frame reasons** ("this expression depends on variable
`_pyobj_state`, which is left out in the specification"), which is why the route needed
HONEST frames on both functions to surface. A guard that hides a defect is not a guard that
stops it.

**THE REFUSAL WAS LANDED AND THEN REVERTED, and the measurement that removed it is the
lesson.** Before landing it I censused the blast radius over the CORPUS and
`src/pycsl_lib` — zero hits — and not over the two trees that must verify:

    src/self-annotate/src    14 functions read the same `getattr` twice with an intervening call
    src/pycsl               212 functions do

because `getattr(self, "_x", {})` and `getattr(args, …)` are how this compiler reads
optional attributes. **The mirror stopped emitting (44 of 53 sources)** and four
emission-dependent planes went red — which I first misdiagnosed as contention, since the
battery really had been sharing twelve cores. Re-running the emission ALONE gave the same
44 and named the real cause. With the refusal reverted: **53 of 53**, and all four planes
green (`bespoke-model-drift` back to its true population of 27 hand-synthesized models).

Narrowing did not save it either: restricting to a non-`self` receiver that is an
`Any`/unannotated PARAMETER still leaves 12 live and 4 mirror hits — including
`pycsl.py::_run_pipeline`, the very function the refusal was written into. **What separates
the route from the idiom is the receiver's static CLASS (`_ga_cls`), which only Module 6
knows.**

So the route is OPEN, its two carriers (no-default and three-argument spellings) live in
`getting-better/open-routes/` and are run by `bin/check-open-route-carriers.py`, and the
control 1727 stays in the corpus.

**The faithful fix is a state-keyed device** — `val function pycsl_getattr_missing_<h> (s:
int) : int` applied to `!_pyobj_state` — which keeps #197's equality for two reads with no
intervening write and loses it exactly across one. It changes emission in
`module6_whyml/expressions.py`, which is mirrored UN-trusted, so it costs a verbatim mirror
edit, that file's whole-file re-proof (21347 goals) and a corpus byte-diff. **Price
recorded; this window took the refusal**, at the IR seam beside #200/#204, keyed on exactly
the false-equality shape, with the blast radius measured at ZERO before landing (no
function in the corpus or in `src/pycsl_lib/` reads the same `getattr` expression twice in
a function that also calls something else).

**And then my own refusal missed a spelling** (witness 1728): it was keyed on `len(args) <=
2` because 1726 used the no-default form, while the THREE-ARGUMENT form has the identical
defect — an unknown receiver takes the per-site constant whether or not a default is
written. Second time in one day (route #208 was the first, twenty minutes after #206), same
cause both times: the guard was derived from the shape of the witness instead of from the
property. Carriers `route213-carrier-*.py` (both PROVE today, outside the corpus); control 1727 (PASS, #197's equality preserved).

## Route #214 — OPEN. The other arm: one constant for two different receivers

```python
#@ ensures \result == 0
def f(o: Any, p: Any) -> int:
    d = getattr(o, "a", {})
    e = getattr(p, "b", {})
    if d == e:
        return 0
    return 1
```

**PROVED**, emitting `pycsl_getattr_default_142644979` for BOTH reads — different objects,
different attribute names, one constant. CPython answers **1** for `o.a = {1: 2}`, `p.b =
{3: 4}`, and the TRUE twin `\result == 1` was REFUSED.

Route #197 repaired the SCALAR-default arm. The arm above it, which runs first for a
Dict/Array/Set/Call default, still answers route #47's DEFAULT-KEYED constant — shared
across sites by design, because two syntactically identical defaults denote equal values.
For an UNKNOWN receiver that design turns "both reads returned their default" into "both
reads are the same value".

### Both repairs were measured, and both are blocked

* **The faithful one** (use the per-site device when the class is UNKNOWN) was implemented
  and **reverted**: it breaks corpus **1073**, route #47's own granularity control, whose
  claim `getattr(c, "missing", {}) == getattr(c, "other", {})` is TRUE of CPython (both
  absent → both `{}`). The cause is measurable with `PYCSL_GETATTR_CENSUS=1`: `c = C()` is
  typed `Any`, so a local of a KNOWN class classifies as UNKNOWN. **The repair is blocked
  on local-type inference for constructor-assigned locals.**
* **A refusal** keyed on "collection default on an `Any`/unannotated PARAMETER receiver"
  was measured before being written: **104 such sites**, nearly all in
  `src/self-annotate/` — the mirror itself, which must verify.

### Why there is no corpus witness, and what runs the carrier instead

The carrier PROVES today. `# pycsl-expected: FAIL` would be an XPASS — a red suite, by the
rule that exists precisely to catch a negative witness that starts proving — and
`PASS` would write "this false proof is expected" into the corpus. So the carrier sits at
`getting-better/open-routes/route214-carrier-two-unknown-receivers.py` and
`bin/check-open-route-carriers.py` runs it, asserting the recorded verdict and saying that
a CHANGE means the route is probably closed and the entry must go in the same commit.
