# Route #222 (CLOSED same day) — an `@overload` stub's `#@ requires` went nowhere and said nothing

**Found:** 2026-09-23, gen #31, by walking the early RETURNS of
`Module5_IREmitter.visit_FunctionDef` — the same dispatcher whose FIRST early return was
route #219. There are exactly two: the dunder skip, and the `@overload` stub.

## The decisive pair

```python
#@ requires x > 100
@overload
def f(x: int) -> int: ...

#@ ensures \result == x
def f(x: int) -> int:
    return x

#@ ensures \result == 0
def use() -> int:
    return f(0)          # plainly violates the declared precondition
```

    [+] Verification SUCCESS! All contracts formally proven.

Move the identical `#@ requires x > 100` to the IMPLEMENTATION and `f(0)` is correctly
refused. The precondition machinery was never broken; it was bypassed by WHERE the clause
was written.

The emission settles what happened — the clause is not weakened, it is ABSENT:

```
  let f (x: int) : int
    ensures  { (result = x) } (* linear *)
  =
    x
```

## The mechanism

`_synthesize_overload_guard` reads `node.csl_ensures` and nothing else. Each `#@ ensures Q`
becomes `isinstance(p, T) ==> Q` on the implementation; the stub node is then discarded
(`return` in `visit_FunctionDef`). A `#@ requires`, `#@ assigns`, `#@ raises`,
`#@ no_exception`, `#@ diverges` or `#@ variant` on a stub is read by the parser, attached to
the AST node, and thrown away with it.

## Sound, and still wrong to be silent

Dropping a PRECONDITION proves the callee under a WEAKER assumption: the body must discharge
its own postcondition without it (measured — it does, or the file fails), and no caller gains
anything false. So this is NOT a soundness route by the "a false contract proves" standard,
and it is recorded as one anyway for the reason routes #216 and #219 are: **the tool prints
`All contracts formally proven` over a module in which a contract the user WROTE is enforced
nowhere.** That sentence is the product's central claim, and a clause that evaporates without
a word is the most direct way to make it false.

## Why nothing caught it

`@overload` appears in **ZERO corpus files**. The construct has an implementation
(`_is_overload_stub`, `_synthesize_overload_guard`, `_build_overload_param_guard`,
`_overload_type_name`), a careful documented lowering in the concrete-syntax reference, and
no witness of any kind. `bin/check-clause-survival.py` — the plane built precisely to catch
a declared clause that does not survive to the emission — can only measure files that exist.

And the documentation is the second half of the answer. Its `@overload` section describes the
`ensures` path in detail and says nothing about the other clauses. **That is how a discarded
clause survives: the documentation describes what IS carried, and the reader supplies the
rest.**

## The repair (landed)

REFUSED, not carried. `PYCSL-SEM-OVERLOAD-CLAUSE-DISCARDED` fires when a stub carries any of
`requires` / `assigns` / `raises` / `no_exception` / `diverges` / `variant` / a loop or class
invariant, and its message names the fix (move the clause to the implementation, where it is
enforced at every call site). Carrying a precondition into a guarded family is a real design
question — which arm's guard should it hide under? — and a refusal is not the place to answer
it.

**IT LIVES AT `_run_pipeline`, NOT AT `visit_FunctionDef`, AND THE FIRST DRAFT DID NOT.**
The natural home is the early return itself. Placed there, the refusal adds a `raise` to a
LIVE function whose MIRROR twin is `\trusted` and declares no `#@ raises` — and
`check-trusted-raises-honesty` went 62 -> 64 SILENT, because TWO mirror files carry a
`\trusted` stub named `visit_FunctionDef`, so ONE new raise counted twice. Honouring it would
have meant a `#@ raises` edit on both stubs plus the re-proof of every mirror that calls
them, and an emission delta (`exception PyCSLSemErr222` + `raises { ... }`) that a sweep
caught in `frontend/__init__.mlw`.
`_run_pipeline`'s own mirror twin is `\trusted` AND ALREADY IN THAT POPULATION, so the
refusal there costs no marker, no emission move, no new definition and no new honesty entry:
the CHOKE-POINT RULE, the same reasoning routes #206-#215 used. The price is that the clauses
must be read off the SOURCE TEXT rather than the AST — a `#@` line is a comment — exactly as
route #216's `conforms_to` scan already does two blocks above it.

THE MEASUREMENT THAT MADE THE DIFFERENCE VISIBLE was a plane, not a reading: the first
placement passed fidelity, passed the corpus byte-diff (0 MOVED over 1328 files) and still
moved a trust-honesty ratchet by two. A byte-diff over the CORPUS cannot see a cost that
lands in the MIRROR.

CENSUS BEFORE LANDING: `@overload` occurs in 0 corpus files, 1 mirror, 3 live and 1
`pycsl_lib` source, and NONE of them puts a non-`ensures` clause on a stub. Byte-inert by
measurement rather than by construction.

## Witnesses — and 1835 is the first corpus file to exercise `@overload` at all

* `1834_gen31_overload_stub_requires_is_refused.py`       — expected FAIL (the carrier)
* `1835_gen31_overload_stub_ensures_still_carried.py`     — expected FAIL, on the SYNTHESIZED
  guarded postcondition rather than on a refusal. If it ever starts being REFUSED, the repair
  has become a ban on the feature.
* `1836_gen31_overload_requires_on_the_implementation.py` — expected FAIL, the same
  precondition correctly placed; this is what makes #222 a route and not a missing feature.
