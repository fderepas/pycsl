"""Test 1214 — ROUTE #79, THE WIDEST FORM OF THE DEFECT, AND THE ONE NO CENSUS FOUND.

`_collect_init_construction` computed the parameter set and then did:

    pset = set(init_params) | set(kwonly_params)
    if not pset:
        break                      # <-- a PARAMETERLESS `__init__` never reached the scan

So a constructor taking no arguments at all never had a single field initialiser examined,
and EVERY computed field it set took `_field_default`'s literal `0`. Measured at HEAD:

    K: int = 8
    class C:
        x: int
        def __init__(self) -> None:
            self.x = K + 1

    C().x               #@ ensures \\result == 0     <-- PROVED; CPython returns 9

**THIS CARRIER IS INVISIBLE TO ANY CENSUS THAT STARTS FROM THE CAPTURE RULE**, because the
capture rule is never reached — the early `break` happens first. Route #79's recorded census
applied "the complement of the live capture rule" and so could only ever enumerate
constructors that HAD parameters. The repair is therefore placed BEFORE the `break`, and
this file is the witness for that placement specifically.

THE GENERALISATION WORTH KEEPING: **A GUARD'S EARLY EXIT IS PART OF THE GUARD, AND A CENSUS
WRITTEN AS "THE COMPLEMENT OF THE RULE" SILENTLY EXCLUDES EVERY INPUT THAT NEVER REACHED THE
RULE.** Ask what returns early, not only what the predicate rejects.

This file is `pycsl-expected: FAIL`: the claim is FALSE of the program and must not prove.
"""
# pycsl-expected: FAIL

K: int = 8


class C:
    x: int

    #@ assigns self.x
    def __init__(self) -> None:
        self.x = K + 1


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.x
