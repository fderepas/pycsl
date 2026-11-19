# Check 1 is a quarter of the conversion criterion, and the other three quarters are executable

Generation #31, 2026-09-26T00:10Z. Written from six failures, all of them this session's.

## What check 1 is, and exactly where it is blind

The criterion this session sharpened over four commits reads, in full:

> Diff the emitted `.mlw` before and after retiring the marker. A new abstract `val` may not
> erase an EFFECT or an INPUT DEPENDENCE (a nullary op erases the dependence; an op with no
> `writes` standing for a mutation erases the effect). **Clause 4:** the conversion must MOVE
> A CLAUSE from ASSUMED to PROVED — a zero-line emit-diff is the limiting case and is refused.

It is a good criterion. It refused `_cache_root` (a nullary `root_mkdir_0 ()` standing for
`os.mkdir`), `validate_ir` (twenty new ops, three of them nullary where the input belonged),
`_Parser._max_end` and several others, each time naming the mechanism.

**And it admitted all six of the hollow conversions.** Here is the gap, stated precisely:

> Check 1 audits the NEW ABSTRACT OPS. An erasure that happens WITHOUT A NEW OP is invisible
> to it.

All five vacuity failures are of that kind. `error(self, msg)` introduces no new `val` at all:
the message f-string lowers to a hash CONSTANT, which is not an operation, takes no argument,
and appears in no ledger. The emitted body simply never mentions `msg`. Likewise
`stable_hash(s)` — `stable_hash("String") = 1153884070` is a constant folded from a literal.
And `iter_fields`'s `yield field, getattr(node, field)` becomes `let _ = (any int) in ()`:
`any int` is a Why3 EXPRESSION, not a declared `val`, so the op ledger stays empty while the
generator's entire meaning is discarded.

Check 1 reads a DIFF OF DECLARATIONS. Three of the four ways a body can be hollow live in the
BODY.

## The criterion, restated as it should have been applied

A `\trusted` marker may be retired when ALL of these hold. The first is read by a human from an
emit-diff; the other four are programs, and they take about four minutes to run.

| # | check | instrument |
|---|---|---|
| 1 | no new op erases an EFFECT or an INPUT DEPENDENCE; a clause MOVES from assumed to proved | emit-diff, read |
| 2 | the emitted body USES the inputs the live body uses | `bin/check-emitted-vacuity.py --emit` |
| 3 | a generator's yielded VALUES survive | `bin/check-yield-erasure.py` |
| 4 | the CALLERS can see the body (no `val self__<m>_<n>` shadow) | `bin/check-shadowed-selfcalls.py` |
| 5 | the function is emitted as a DEFINITION, not re-abstracted | `bin/check-untrusted-emitted.py` |

plus CHECK 0 (static: no un-trusted closure inside a `\trusted` parent) and the three L-planes
(fidelity, proof, corpus byte-inertness) that gate the increment as a whole.

Checks 2, 3 and 4 are all in `bin/run-soundness-planes.sh --slow`, which is one flag, and this
session ran the battery twenty-eight times without it.

## Why "it proved" is the weakest evidence in the list

Every one of the six PROVED. Four of them proved a contract of the form
`requires { true } ensures { true }` plus frame clauses, over a body that computes nothing from
its arguments. A proof is a statement about the EMITTED program; the question a conversion asks
is whether the emitted program still stands for the Python one. Those are different questions
and only the second one is the campaign's.

The cheapest possible summary, and the one to carry forward:

> **A green proof and a clean emit-diff say the conversion is WELL-FORMED. Whether it is WORTH
> ANYTHING is measured by four other programs, and they cost four minutes.**

See `finding-eleven-gates-over-four-red-oracles.md` for the six, and wall-lesson (q6).
