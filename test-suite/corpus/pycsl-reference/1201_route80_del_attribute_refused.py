"""Test 1201 — ROUTE #80: `del <obj>.<attr>` (an ATTRIBUTE delete) is REFUSED.

THIS IS ROUTE #77's OWN RESIDUE, AND THE RESIDUE WAS HALF WRONG. #77 closed the SLICE
delete at `Module5_IREmitter._py_stmt_delete` and filed `del name` and `del obj.attr`
together as the lower-value half, out of scope "because the program raises". That
reasoning is CORRECT for `del name` (a later read is `UnboundLocalError`) and FALSE for
`del obj.attr`, because Python's attribute lookup FALLS BACK TO THE CLASS ATTRIBUTE. The
program then runs to completion and returns a DIFFERENT value, which puts it squarely in
the #69 class: a false postcondition about ordinary, TOTAL Python, with no `no_exception`
and no opt-in.

Measured, before this refusal:

    class C:
        x: int = 5                   # the class attribute — the fallback
        def __init__(self) -> None:
            self.x = 10              # the instance attribute shadows it

    c = C(); del c.x; return c.x
    #@ ensures \\result == 10         <-- FALSE OF THE PROGRAM (Python returns 5)

    [+] Verification SUCCESS! All contracts formally proven.

BOTH DIRECTIONS, ON THREE CARRIERS — which is what makes it a route and not a gap:

    carrier                          claim               CPython   PyCSL
    direct read (this file)          \\result == 10       5         PROVED
    direct read, TRUE twin           \\result == 5        5         refused
    arithmetic `c.x - 5` (1202)      \\result == 5        0         PROVED
    arithmetic, TRUE twin            \\result == 0        0         refused
    `requires` discharge (1203)      requires v == 10    v is 5    PROVED
    `requires` discharge, TRUE twin  requires v == 5     v is 5    refused

The third carrier is the ESCALATION: the stale field value DISCHARGES A CALLEE'S
PRECONDITION at a call site whose `requires` is FALSE at runtime, so the defect propagates
across the call graph rather than staying local to one clause.

MECHANISM: the same site as #77 — `_py_stmt_delete` appended `{"stmt": "Pass"}` for every
non-Subscript target, so the delete is erased and the later read is constant-folded from
the `__init__` store.

LESSON, banked because it cost a generation: **"OUT OF SCOPE BECAUSE THE PROGRAM RAISES"
IS ITSELF A CLAIM ABOUT PYTHON, AND IT MUST BE PROBED RATHER THAN REASONED ABOUT.** One
language feature — class-attribute fallback — turned a non-total residue into a total
soundness route. The whole `del name` / `del obj.attr` family was written off in a single
sentence and half of it was live.

CENSUS: ZERO attribute deletes across `test-suite/corpus/`, `src/self-annotate/`,
`src/pycsl/` and `src/pycsl_lib/` (3636 files parsed), so the guard is byte-inert BY
CONSTRUCTION — it only RAISES or FALLS THROUGH and never alters emitted text. `del name`
stays the unmodelled no-op (corpus 0173 keeps its verdict); the subscript locks 0854-0857,
0985, 1154 and 1155 and the #77 slice locks 1194-1197 all keep theirs.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


class C:
    x: int = 5

    #@ assigns self.x
    def __init__(self) -> None:
        self.x = 10


#@ requires True
#@ ensures \result == 10
#@ assigns \nothing
def f() -> int:
    c = C()
    del c.x
    return c.x
