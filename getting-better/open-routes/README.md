# OPEN ROUTES — exploited, reproduced, NOT closed (relaunch #45)

Everything in this directory is a **live unsoundness with a working reproduction**.
Each file PROVES a contract that is FALSE of its own program, at HEAD, in the DEFAULT
`hoare` memory model, with no flags. They are kept HERE rather than in
`test-suite/corpus/pycsl-reference/` for one reason: a corpus witness for an open route
would be an **XPASS**, which the harness has counted as a failure since relaunch #44.
Move each file into the corpus in the SAME increment that closes its route.

## ROUTE #35 — CLOSED (relaunch #45, later the same window). Kept for the record.

The obstacle described below was real and the fix that overcame it is in
`module6_whyml/expressions.py`: separate PYTHON-BOOLISHNESS (does `1`/`0` already
encode the Python value faithfully?) from WHY3 TYPING (may this operand be selected
raw, or must it be wrapped back to an int?). `left_b == f"({left} <> 0)"` is the
precise second test. Mirror L3-tc came back 53/53, sixteen mirror emissions moved,
and their re-proofs were run. Witnesses are now `pycsl-reference/1023`-`1024`.

### The original entry, unedited:

## ROUTE #35 — `and`/`or` in a VALUE position return a boolean, not the operand

    x = 0 or 5      # Python: 5     model: 1
    x = 3 and 7     # Python: 7     model: 1

`module6_whyml/expressions.py`, the `raw_op in ("and","or")` branch, ends in
`return f"(if {left_b} {op} {right_b} then 1 else 0)"` under a comment that says "In
body context, Python's and/or return int". They return an OPERAND. The lowering is
CORRECT IN A CONDITION and WRONG IN A VALUE, and nothing at the emission site knows
which consumer it has. The string-operand and emit_ir-operand cases immediately above
it ALREADY select the operand — the general case never caught up.

REPRODUCTIONS: `route35-shortcircuit-value.py` (false, proves) and
`route35-shortcircuit-value-faithful.py` (true, does not prove).

### Why it is not closed here, MEASURED rather than guessed

* The value-preserving form
  `(let __or_l = <l> in if __or_l <> 0 then __or_l else <r>)` moves **19 of the 53
  mirror emissions**, including `expressions.py` (20125 goals, ~4h),
  `frontend/pure_ast`, `Module5_IREmitter`, `statements`, `stmt_control_flow`,
  `Module6_WhyMLTranspiler` and `preamble`. That is 19 whole-file re-proofs.
* AND THE NAIVE FORM IS ILL-TYPED. `_to_bool` returns a Why3 **bool** from many of its
  branches (a comparison, `Array.length … <> 0`, `hval_truthy …`, `py_isinstance_…_op`,
  an inductive predicate) and an **int** from exactly one (`({x} <> 0)`, its default).
  Selecting on the raw operand therefore emits `bool <> 0`: measured, the first version
  took mirror L3-tc from 53/53 to **40/53**, and the spike proof
  `frontend/module_collect` failed with "This expression has type bool, but is expected
  to have type int".
* PYTHON-BOOLISHNESS AND WHY3 TYPING ARE DIFFERENT QUESTIONS and the fix needs both:
  the first decides whether the `1`/`0` encoding is already faithful (it is, for a
  chain of comparisons — Python returns `True`/`False` there and `1`/`0` encodes it
  exactly, which is what keeps the ordinary `a == b or c == d` shape byte-inert); the
  second decides whether an operand may be selected raw or must be wrapped with
  `(if <bool> then 1 else 0)`. `left_b == f"({left} <> 0)"` is the precise test for the
  second. A THIRD trap is already documented in the code: the boolishness test must
  RECURSE through nested `and`/`or`, or `a == 0 and b == 3 and c == 1` looks like
  "int on the left, bool on the right" — the first version refused six real corpus
  files (0290, 0900, 0901, 0935, python-reference 0158/0161) because of it.

### The capability, named

Reconcile the two tests as above, then pay the 19 re-proofs. Estimated 8-12h wall at
two concurrent proofs. This is a COST/SCALE boundary in the §A.3 sense, not a
correctness one — every piece is expressible and the obstacles are enumerated here.

## ROUTE #36 — CLOSED for the index-valued loop (relaunch #45). Kept for the record.

The refusal described below was the wrong instrument and the entry stands as a record of
why. What landed instead is a WRITE-BACK in the binder: assign the OUTER ref immediately
before opening the inner `let`. It reproduces Python exactly, never-ran case included, it
is scoped to targets the function reads outside their loop AND to index-valued loops
(where the bound term is the counter and is int-typed like the outer ref), and it moves
**zero** mirror emissions and **zero** corpus emissions — so it cost no re-proofs at all,
against the fourteen the refusal implied. Witnesses `pycsl-reference/1025`-`1026`.

RESIDUE, recorded rather than hidden: `for x in <sequence>` followed by a read of `x`
still yields the pre-loop value. A general element write-back is NOT well-typed — the
outer ref takes its type from the FIRST assignment to that name, which need not be the
loop's element type. Measured: an unconditional write-back took mirror L3-tc to 51/53
(`expressions.py`, `functions.py`) and an `any int` havoc to 52/53 (`stmt_control_flow.py`,
whose loop target ref is `emit_ir`). Closing the residue needs the outer ref's declared
type at the binder, which it does not have.

### The original entry, unedited:

## ROUTE #36 — the `for` loop variable does not survive the loop

    i = 0
    for i in range(3):
        pass
    return i        # Python: 2      model: 0

The body opens `let i = ref (!_idx_i) in` INSIDE the loop, so the name is shadowed and
the OUTER `i` still holds its pre-loop value afterwards. Python leaves a loop variable
bound to its LAST value.

REPRODUCTIONS: `route36-loop-var-leak.py` (target pre-assigned) and
`route36-loop-var-leak-no-preassign.py` — BOTH prove. The second matters: a first guess
was that the exploit needs a stale pre-loop value, and it does not, because Module 6
declares the loop target as an outer `ref 0` regardless.

### Why it is not closed here, MEASURED rather than guessed

A pipeline-level REFUSAL of "the `for` target is read outside its loop" is written and
kept in `route36-refusal-that-broke-14-mirrors.py.txt`. It works, and it **breaks the
self-annotation mirror**: 14 of the 53 mirror files stop emitting, because reading a
loop variable after its loop is an ordinary Python idiom the emitter itself uses
throughout. A gate that makes the tool unable to verify itself is not shippable, and
exempting the mirror from its own soundness check is exactly the move this campaign
refuses.

One narrowing was tried and rejected on evidence: "refuse only when the target is
ASSIGNED before the loop" leaves `route36-loop-var-leak-no-preassign.py` exploitable.

One EXCLUSION in that refusal is worth keeping in any future version: a Python `assert`
is DROPPED by Module 6 (measured on `python-reference/0177`, whose `assert i == 5`
after a `break` loop emits nothing at all), so a read inside one is not a leak — and
counting it fails a PASSING corpus test for no soundness gain.

### The capability, named

Bind the OUTER ref in the loop body (`i := !_idx_i`, or `i := <elem_expr>` for a
non-range iterable) instead of shadowing it. That reproduces Python exactly INCLUDING
the never-ran case, where the variable keeps its previous value. It moves every
for-loop emission that reads its target afterwards — the same 14 mirror files — so it
carries the same 14 whole-file re-proofs. Do it in the same funded increment as #35;
the two overlap heavily in the files they touch.
