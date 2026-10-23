"""Test 1300 — ROUTE #107's repair is guarded STRUCTURALLY, not by spelling.

The repair lowers a try's `else:` as a sibling of the try/except behind a completion flag.
A flag is a new name in the emitted WhyML, and inventing a name that a user might also
choose would have reproduced the very defect being repaired — so the flag carries a PRIME
(`try_else_ok'<depth>`), which `whyml_ident` can NEVER produce: a Python identifier cannot
contain `'`, and the non-ASCII sanitiser maps to letters or to `u<ord>`.

This file NEGATIVE-TESTS that guarantee by naming a user local exactly `try_else_ok`, and
keeping `praiseworthy` alongside it. Both survive into the model and the TRUE postcondition
proves. Emitted (verbatim):

    let try_else_ok = ref 0 in          <- the USER's local
    let try_else_ok'4 = ref False in    <- the synthetic flag, distinct by construction
    ...
    if !try_else_ok'4 then begin
      y := 5; try_else_ok := 0; praiseworthy := 0
    end;

NEGATIVE-TEST EVERY NEW GATE BY REMOVING THE THING IT SHOULD CATCH — here, by writing the
one name that could collide with it.
"""
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    y = 0
    try:
        y = 1
    except ValueError:
        y = 9
    else:
        y = 5
        try_else_ok = 0
        praiseworthy = 0
    return y
