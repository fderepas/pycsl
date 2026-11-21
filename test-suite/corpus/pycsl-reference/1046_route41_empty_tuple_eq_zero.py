"""Test 1046 — ROUTE #41, the last shape: an EMPTY tuple compared to 0.

FALSE OF THE PROGRAM: `() == 0` is False in Python, so this returns 0.

Routes #25/#26/#27 recorded an erased local only when the set/tuple literal was
NON-EMPTY (`val_ir.get("elts")`), and that guard is exactly right for the consumer it
was written for: an EMPTY container IS falsy, so the literal `0` is the FAITHFUL truth
value and refusing it would have been a completeness loss for nothing.

It is wrong for the VALUE. `() == 0` is False and the literal `0` makes it decidably
TRUE, so at the parent commit d1dabea5 `\result == 7` PROVED.

THE RECORD IS NOW MADE FOR THE EMPTY LITERALS TOO, under a `#empty` suffix that
`_to_bool` skips: the truthiness stays faithful and unrefused, while the route-#41
opaque READ fires on every recorded name. One dict, two consumers — deliberately not a
second attribute, which would have moved `bin/check-mirror-field-parity.py` and owed a
mirror field declaration.

The price is measured and accepted: `x = (); if x: return 7` no longer proves
`\result == 0`, because the read is now opaque. That is a completeness loss on a
correct case, and the alternative — leaving the value decidable so that one guard keeps
proving — is what this route is about.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = ()
    if x == 0:
        return 7
    return 0
