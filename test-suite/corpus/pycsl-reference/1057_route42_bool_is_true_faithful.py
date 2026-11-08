"""Test 1057 — ROUTE #90: this file's own claim is FALSE, and it is now a NEGATIVE witness.

WAS: a route #42 WHITELIST control asserting `<bool> is True` is FAITHFUL and PROVES.
IS:  the carrier that shows route #42's admitted arm was UNSOUND.

NOT TRUE OF THE PROGRAM. The precondition is `b == True`, and in Python `1 == True` is
True — so `f(1)` SATISFIES this precondition. But `1 is True` is **False** (`True` is a
distinct singleton object from the int 1), so `f(1)` returns **0**, not 7. The
postcondition `\result == 7` is therefore FALSE for a caller that meets the stated
requirement, and MEASURED under CPython: `f(True) = 7` but `f(1) = 0`.

The old docstring argued this was "the half of route #42 that must NOT be refused", on
the ground that "for a genuine `bool`, `b is True` and `b == True` agree". That premise
is fine; the error was believing the ANNOTATION `b: bool` establishes it. It does not —
`_build_function_symbol_table` records a DECLARATION, and route #51 had already proved
an annotation in this codebase is not a fact.

THE PART WORTH KEEPING AS A LESSON: the old docstring ended "it fails if the whitelist is
ever narrowed to nothing (a refusal that refuses everything is not a fix)". That is a
RATCHET AGAINST THE REPAIR — a corpus control written to prevent over-narrowing became
the thing that protected an unsound arm for 48 routes. A control that pins a CAPABILITY
must state what makes the capability SOUND, not merely that it exists.

The genuine, sound half of the whitelist is untouched and still admits `(a > b) is True`
and `True is True` directly; re-admitting a VARIABLE that HOLDS such a value is a
completeness follow-up recorded on the ladder, not a soundness claim.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires b == True
#@ ensures \result == 7
#@ assigns \nothing
def f(b: bool) -> int:
    if b is True:
        return 7
    return 0
