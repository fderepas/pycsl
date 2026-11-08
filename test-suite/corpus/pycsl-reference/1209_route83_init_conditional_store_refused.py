"""Test 1209 — ROUTE #83: a field stored INSIDE CONTROL FLOW in `__init__` is UNCONSTRAINED.

`_collect_init_construction` only ever considered the TOP-LEVEL statements of `__init__`,
by its own docstring's reasoning that *"a conditional/looping init can't be reduced to a
single record literal"*. That reasoning is correct about the REPRESENTATION and says
nothing about what the field's value then IS — the field fell through to `_field_default`
and got a literal `0`, a DEFINITE FALSE FACT the emitter then proved things from.

Measured, before the repair:

    class C:
        v: int
        def __init__(self, n: int) -> None:
            self.v: int = 0
            if n > 0:
                self.v = n

    C(7).v      #@ ensures \\result == 0      <-- PROVED; CPython returns 7

FOUR CARRIERS, and the second one is why the census's predicted mechanism was WRONG:

    annotated store inside `if`      \\result == 0   CPython 7   PROVED / twin refused
    UN-ANNOTATED store inside `if`   \\result == 0   CPython 7   PROVED / twin refused
    store inside a `while`           \\result == 0   CPython 7   PROVED
    the stale 0 DISCHARGES a callee's `requires m == 0` where the runtime value is 7

The carve-out census that led here predicted an ANNOTATION-specific hole (`desugar.py`
protects every `AnnAssign` inside `__init__`, and `_py_stmt_annassign` has no `else` for
an Attribute target). **Both halves of that are TRUE, and the annotation is IRRELEVANT** —
the un-annotated control proves the same false claim. Building the repair the candidate
described would have fixed the annotated spelling, left the commoner un-annotated one wide
open, and passed every gate. **A CENSUS CANDIDATE'S MECHANISM STORY IS A HYPOTHESIS,
SEPARATE FROM ITS EXISTENCE, AND THE CONTROL IS WHAT SEPARATES THEM.**

THE REPAIR EMITS AN UNCONSTRAINED VALUE, NOT A REFUSAL, and it OVERRIDES any captured
value, because a conditional store can overwrite whatever the straight-line prefix put
there. So BOTH `\\result == 0` and `\\result == 7` are now unprovable — which is the
HONEST outcome rather than a regression: the model genuinely cannot know which branch ran.

Contrast route #82, where the constructor parameter WAS recoverable and the repair is a
FAITHFUL CAPTURE that made the true claims provable. **Prefer a faithful capture wherever
the information exists; fall back to unconstrained only where it genuinely does not.**

Blast radius measured before building: 5 nested stores repo-wide, ALL in `src/pycsl_lib`,
ZERO in the verified corpus, the mirror and the compiler — and the byte-diff confirms it,
976/976 and 2203/2203 with 0 MOVED / 0 GONE / 0 APPEARED.

This file is `pycsl-expected: FAIL`: the claim is FALSE of the program and must not prove.
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
