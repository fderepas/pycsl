"""Test 1119 — ROUTE #53 negative witness (c): the ORDERING was decided too, and this
is the sneakier half.

FALSE OF THE PROGRAM: `0.1 + 0.2` is `0.30000000000000004`, so `0.1 + 0.2 <= 0.3` is
`False` in Python. Over the exact reals the sum IS three tenths, so `<=` holds and
the goal closed.

MEASURED ASYMMETRY, and it is why an equality-only reading of this route is wrong.
The route's own record noted that the float ORDERING form "fails closed today",
which was measured on the TRUE direction: `\result > 0.3` — true of the program —
does not prove, a completeness gap. The FALSE direction is the one that matters and
it went the other way: `\result <= 0.3` PROVED. So the model was UNSOUND in the
direction that asserts something false and INCOMPLETE in the direction that asserts
something true, which is exactly the wrong way round, and checking only the
fails-closed direction would have certified the ordering as safe.

An uninterpreted sum decides neither direction, so this now fails closed with its
true-direction twin.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result <= 0.3
#@ assigns \nothing
def f() -> float:
    return 0.1 + 0.2
