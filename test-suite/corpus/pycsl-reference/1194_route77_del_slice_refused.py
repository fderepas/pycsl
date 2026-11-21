"""Test 1194 — ROUTE #77: `del <seq>[i:j]` (a SLICE delete) is REFUSED.

This is route #17's defect ONE STEP OVER, and the step CROSSES A MODULE BOUNDARY. #17
closed the ELEMENT delete (corpus 0985) with a refusal in `module6_whyml/statements.py`,
but that guard is a BLOCKLIST KEYED ON THE EMITTED STRING (`if code.strip() == "()"`), and
the slice form never reached it: `Module5_IREmitter._py_stmt_delete` dropped `del seq[i:j]`
to a literal `{"stmt": "Pass"}` one stage EARLIER, byte-indistinguishable from a user's
`pass`. So the guard and the hazard lived in different modules and the blocklist failed
OPEN. Measured, before this refusal:

    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return xs[0]
    #@ ensures \\result == 1             <-- FALSE OF THE PROGRAM (Python returns 3)

    [+] Verification SUCCESS! All contracts formally proven.

Why3 printed `unused variable xs` on that same run — the delete is erased and the read is
then constant-folded, so the list never reaches the solver at all.

BOTH DIRECTIONS WERE MEASURED, which is what makes it a route and not a gap: the TRUE twin
of this program (`#@ ensures \\result == 3`) is REFUSED while the false one PROVED. Three
carriers proved a false claim — this element read, the `len()` read (1195) and `del xs[:]`
(1196) — and the stale value also DISCHARGED A CALLEE'S `requires` at a call site (1197),
so the defect propagated across the call graph rather than staying local to the clause.

REFUSED rather than modelled, for route #17's reason: Python's slice `del` removes a whole
range, shifting every later element left and SHRINKING the sequence, so a faithful model
needs the LENGTH as part of the value model, and a wrong shift is worse than no shift.

THE ONE-TOKEN ALTERNATIVE WAS REJECTED BY MEASUREMENT. Merely dropping the `not
isinstance(slice_node, ast.Slice)` conjunct would route the slice form into the existing
`DelSubscript` path and let #17's refusal fire — but for a LOCAL DICT receiver that path
does NOT fall through to the `()` no-op: it emits a faithful `map_update_none` keyed on a
coerced slice, i.e. it would MODEL `del d[i:j]` as a key delete where CPython raises
`KeyError`. That trades an old wrong model for a new one.

CENSUS: ZERO slice-deletes in either verified corpus, in the self-annotation mirror, in
`src/pycsl/` and in `src/pycsl_lib/`, so the guard is byte-inert BY CONSTRUCTION — it only
RAISES or FALLS THROUGH and never alters emitted text. Corpus 0854-0857, 1154 and 1155 (the
dict item-delete locks) and 0985 (the #17 element-delete lock) all keep their verdicts.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return xs[0]
