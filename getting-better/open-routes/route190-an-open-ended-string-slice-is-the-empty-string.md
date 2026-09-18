# ROUTE #190 — an open-ended or negative string slice is the EMPTY string

**Status: REPAIR DRAFTED by gen #29 (worktree wtAJ, branch wip/g29-r190, on top of #189).** Severity 1.
Generator: a census of the `ensures` clauses the emitter puts on its abstract ops.

## Measured at `af255fcd` (landed HEAD)

    s = "abc";  t = s[1:];   return len(t)      PROVED  \result == 0   (CPython 2)
    s = "abc";  t = s[0:];   return len(t)      PROVED  \result == 0   (CPython 3)
    s = "abc";  t = s[:-1];  return len(t)      PROVED  \result == 0   (CPython 2)
    s = "abc";  t = s[-2:];  return len(t)      PROVED  \result == 0   (CPython 2)
    #@ requires i == -1
    s = "abc";  t = s[i:];   return len(t)      PROVED  \result == 0   (CPython 1)

TWO defects, and the second is why the first is not merely a bug:

1. **An OMITTED bound is a `None` EXPRESSION, not an absent key.** Every branch of
   `_handle_slice_access_expr` asks `sl.get("upper")` and falls back to the sequence's own
   LENGTH when the bound is absent — the right answer, and DEAD CODE, because the typed
   `SliceExpr` carries an omitted bound as a `None` node, which is truthy and lowers to the
   integer `0` (route #56's None-as-zero, reached through a slice). So `s[1:]` emitted
   `str_sub_op s 1 ((0) - (1))` — a negative length.

2. **The substring bridge decided the answer unconditionally.** `str_sub_op` carried
   `ensures { result = String.substring s lo len }` with no side condition, and Why3's
   `String.substring` answers the EMPTY string whenever `start < 0` or `len <= 0`. So the
   negative length from (1), and every negative index Python would read from the END, was
   not merely unmodelled — it was DECIDED, wrongly. A spelling-keyed fence would not have
   helped: the last carrier above reaches the same place through a parameter.

The emitter already knew about half of this: the string INDEX path refuses to use the
bridge for a negative literal index, with a comment saying `String.substring s (-1) 1`
does not read from the end. The slice path never got the same treatment.

## Repair (draft)

(1) An omitted bound is normalised to a real absence in `_handle_slice_access_expr`, which
restores the length fallback the code already writes — and makes `s[1:]` PROVE its true
length, so this half is a completeness GAIN as well as a soundness fix. (2) `str_sub_op`'s CONTENT law is guarded by
`0 <= lo /\ 0 <= len` — and by exactly that, which is the second thing this route taught.
The first draft guarded it by the LENGTH law's condition
(`… /\ lo + len <= String.length s`) and that is too strong: measured, `"abc"[1:10]` PROVES
`len(t) == 2` at HEAD, because Why3's `String.substring` CLAMPS an overlong length exactly
as Python does. The two disagree in one place only — a NEGATIVE start, where Python counts
from the end and Why3 answers empty — and a negative `len` is the shape a negative STOP
also arrives as (`s[:-1]` is `lo = 0, len = -1`, and Python's answer there is non-empty
while a genuine `hi < lo` is). So the content law now holds wherever the two agree,
including the clamping case, and says nothing where they diverge. The LENGTH law keeps the
full `lo + len <= String.length s` guard, because `String.length result = len` is false in
the clamping case. The in-range content law survives (witness 1671 is discharged by it, not
by a length). The spec plane needs no separate
guard: a slice is not parseable inside a `#@` clause (measured — "expected ')'").

Witnesses 1668, 1669 (XFAIL), 1670, 1671 (PASS controls). Emission: the `str_sub_op`
declaration text changes in 16 corpus and 8 mirror emissions; all 16 corpus files keep
their expectation (13 SUCCESS, and 0768 / 1160 / 1542 are `pycsl-expected: FAIL`).

## One note for the self-verification

`_slice_array_or_opaque` — the only half of the slice handler that IS mirrored — keeps the
`if sl.get("lower")` present-guard, and the mirror models that guard as `true` on the
grounds (its own comment, 07-03-refactor R4) that "the sub-node is always-present in the
model". That was TRUE before this repair and is the same reading that made the defect:
an omitted bound really was always present, as a `None` node. After the repair the guard
is genuinely falsifiable, and the mirror's `true` becomes an OVER-approximation — which
costs nothing, because that function's mirror contract is `requires True / ensures True`
plus a frame. Worth knowing if anyone ever strengthens it.
