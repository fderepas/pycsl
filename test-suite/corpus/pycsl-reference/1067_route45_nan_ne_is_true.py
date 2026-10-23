"""Test 1067 — ROUTE #45 COMPLETENESS control: `nan != nan` is TRUE and now PROVES.

TRUE OF THE PROGRAM: Python returns 7.

Route #45 is the campaign's first repair that makes the model MORE complete as well as more
sound, and this driver is the evidence. Because NaN's comparison semantics are totally
determined — every ordering and `==` False, `!=` True — the lowering is EXACT rather than
opaque, so a true contract the model could not previously discharge now proves. At the
parent commit 3bbfb59f this FAILED.

If a later change replaces the exact lowering with a refusal or an opaque value, this
driver goes red rather than the loss passing unnoticed.
"""
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = float("nan")
    if x != x:
        return 7
    return 0
