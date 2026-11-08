"""Test 1245 — ROUTE #90 OVER-BREADTH CONTROL: the whitelist is NOT narrowed to nothing.

Route #90 deletes ONLY the annotation arm of route #42's `is`-against-a-bool-literal
whitelist. The `Bool` LITERAL arm is untouched and still emits and PROVES, which is what
this driver pins: if a later change refuses everything, this file fails, and "a refusal
that refuses everything is not a fix" becomes executable instead of a docstring.

TRUE OF THE PROGRAM: `True is True` is True in CPython (it is the same singleton object),
so the function returns 7. MEASURED: f() = 7.

Why THIS shape and not a comparison result: see 1246. The comparison and `not` arms are
ADMITTED by the whitelist but emit ill-typed WhyML, and have done so since before route
#90 — so they cannot serve as a positive control. The literal arm is the only admitted
arm that has ever produced a provable emission.
"""
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    if True is True:
        return 7
    return 0
