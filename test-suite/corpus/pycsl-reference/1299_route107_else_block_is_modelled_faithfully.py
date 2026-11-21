"""Test 1299 — ROUTE #107 POSITIVE witness, and the file that BOUNDS the repair.

Byte-identical to 1298 except that the postcondition is the TRUE one. No exception is
raised, Python runs the `else` and returns 5, and this claim must PROVE.

WHY A POSITIVE WITNESS IS REQUIRED AND NOT OPTIONAL. 1298 asserts that something must NOT
prove. An OVER-BROAD repair — one that dropped the `else` a different way, or left its
effect unconstrained — would satisfy 1298 while destroying the capability #33 added. Only a
file that must STILL PROVE can fail when the repair grows too wide.

Note the `praiseworthy` local is KEPT here on purpose: after the repair the block is
lowered structurally and its text is never inspected, so the identifier that used to delete
the block must now be completely inert.
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
        praiseworthy = 0
    return y
