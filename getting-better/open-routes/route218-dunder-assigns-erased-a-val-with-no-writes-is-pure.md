# Route #218 (OPEN) — an explicitly-called DUNDER's `#@ assigns` is erased, and a `val` with no `writes` is PURE

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

## Blast radius (measured, all four populations)

A repair keyed on "an explicit dunder CALL to a dunder that declares `#@ assigns self.<f>`"
touches **exactly one existing file**: `1334_route120_setattr_hook_dropping_a_store.py`,
which is `# pycsl-expected: FAIL`. Corpus-wide there are 9 explicit dunder calls and 3
dunders declaring `assigns self.`; the mirror, the live tree and `pycsl_lib` have 10
explicit dunder calls between them and ZERO writing dunders.

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

The obvious refusal would land on 1334 — **route #120's own witness** — and a refusal that
retires another route's witness is lesson (n3)'s exact failure: the witness stops
witnessing what it was written for, and nothing says so. Deciding that needs 1334 re-run
and its route re-confirmed, and the window did not have the time to verify the
consequence rather than assume it. Recording the defect with its blast radius is worth
more than a repair nobody checked.

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
