"""Test 1210 — ROUTE #83's CONTROL, and it REFUTED THE PREDICTED MECHANISM.

Identical to 1209 except that the conditional store drops its annotation: `self.v = n`
rather than `self.v: int = n`.

This matters because the carve-out census that produced #83 predicted an
ANNOTATION-SPECIFIC hole — `desugar.py` protects every `AnnAssign` inside `__init__` from
the annotated-store normalizer, and `Module5_IREmitter._py_stmt_annassign` has no `else`
for an Attribute target, so an annotated `self.v: int = n` emits no IR at all. Both halves
of that are TRUE and were verified by hand in the source.

**AND THE ANNOTATION IS IRRELEVANT.** This file proved the same false claim and refused the
same true twin. The real cause is one line up: `for stmt in child.body:  # top-level only`.

Had the candidate's repair been built instead — handling the Attribute target in
`_py_stmt_annassign` — it would have fixed the annotated spelling, left THIS one wide open,
and passed every gate green. One control driver, costing two minutes, was the difference.

`pycsl-expected: FAIL`: the claim is FALSE of the program and must not prove.
"""
# pycsl-expected: FAIL


class C:
    v: int

    #@ assigns self.v
    def __init__(self, n: int) -> None:
        self.v: int = 0
        if n > 0:
            self.v = n


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.v
