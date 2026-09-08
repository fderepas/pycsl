"""Test 1057 — ROUTE #42 WHITELIST control: `<bool> is True` is FAITHFUL and PROVES.

TRUE OF THE PROGRAM: for a genuine `bool`, `b is True` and `b == True` agree, so with
`b` required True the function returns 7.

This is the half of route #42 that must NOT be refused, and it is why the fix is a
WHITELIST rather than a type-directed blacklist. A blacklist ("refuse when the operand
is an int-typed Var") would leave every Call-valued and unannotated operand unrefused —
an UNDER-APPROXIMATION, the exact mistake routes #39 and #41 were about. Inverting it
to "admit only what the emitter can SHOW is a Python `bool`" makes this driver the
positive side of the same gate: it exercises the admitted arm, and it fails if the
whitelist is ever narrowed to nothing (a refusal that refuses everything is not a fix).
"""
_ = 0  # anchor
#@ requires b == True
#@ ensures \result == 7
#@ assigns \nothing
def f(b: bool) -> int:
    if b is True:
        return 7
    return 0
