"""Test 1048 — ROUTE #40's RESIDUE: the BUILTIN NAME `Ellipsis` was also the
integer zero, and the FULL SUITE is what surfaced it.

FALSE OF THE PROGRAM: `0 is Ellipsis` is False, so Python returns 0.

Route #40 made the `...` LITERAL opaque. `Ellipsis` — the same singleton, spelled as
a NAME — went through `_py_expr_name`, which returned a bare
`{"type": "Number", "value": 0}` with none of the `py_ellipsis` marker the literal
carries. So the opaque value never reached `x is Ellipsis` and the model still
answered `0 = 0`: at the parent commit 8656942a this proved `\result == 7`.

THE WAY IT WAS FOUND IS THE POINT. Route #40's own witnesses (1036-1040) all pass, the
corpus byte-diff was zero, and every gate was green. What surfaced this was the FULL
REFERENCE SUITE reporting `python-reference/0041` — `x = ...; if x is Ellipsis:` — as a
NEW failure: a TRUE contract that had been proving BY ACCIDENT (`0 = 0`) stopped proving
once half the singleton became opaque. A completeness regression was the visible end of a
live soundness hole.

THE FIX IS ONE AST REWRITE AT A CHOKE POINT: `frontend/desugar.py::normalize_stores` —
a `\trusted` front-end pass — rewrites the Load-context NAME `Ellipsis` into the LITERAL
`...`, which is SEMANTICALLY EXACT (they denote the same object) and lets route #40's
existing opacity cover both spellings. Editing `_py_expr_name` instead would have said
the same thing at the cost of a mirror body sync and a 2109-goal re-proof, because that
method is CONVERTED. The rewrite is skipped entirely if the module BINDS the name
(assignment, parameter, import, def or class), so a program that shadows the builtin
keeps its own meaning.

Both directions are now right: `... is Ellipsis` is `pycsl_ellipsis = pycsl_ellipsis`
(TRUE — `python-reference/0041` proves again, as a capability rather than an accident),
and `<int> is Ellipsis` is `0 = pycsl_ellipsis` (undecidable — this test).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 0
    if x is Ellipsis:
        return 7
    return 0
