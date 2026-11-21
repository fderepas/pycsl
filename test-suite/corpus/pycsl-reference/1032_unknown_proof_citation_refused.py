"""Test 1032 — an unknown `#@ proof` citation is REFUSED, with a message.

`#@ proof rocq <qualname>` imports a Why3 `axiom` whose body comes from Module 6's
hand-curated `_AXIOM_REGISTRY` (78 entries). A citation that is NOT in the
registry must be refused — an axiom nobody can produce a body for cannot anchor
anything.

It always was refused, but by a `NameError`: `PyCSLIRError` is not imported in
`module6_whyml/preamble.py`, so the raise reported `[!] UNEXPECTED PIPELINE
ERROR: name 'PyCSLIRError' is not defined` instead of the message it was written
to give. That is the SECOND internal crash on a refusal path found this window —
`pycsl-reference/0540`, the item the window opened on, was the first. Fail-closed
either way, but a crash is only fail-closed while nothing catches it, and it
tells the reader nothing.

This file pins the refusal: it must FAIL, and it must fail as a `PIPELINE ERROR`
naming the citation, not as an `UNEXPECTED PIPELINE ERROR`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ proof rocq Pycsl.Reference.Totally.Made.Up.false_is_true
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 0
