"""Test 1069 — ROUTE #45 control: every ORDERING against NaN is False, and that is exact.

TRUE OF THE PROGRAM: `float("nan") < 1` is False, so Python returns 0.

The orderings are the half of route #45 that an equality-only fix would have missed, and
they are not merely refused — they are DECIDED, correctly, as `false`. A model that made
them opaque instead would leave this true contract unprovable; a model that left them
reflexive-int would answer them from the opaque int's arbitrary value. At the parent commit
3bbfb59f this FAILED.
"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = float("nan")
    if x < 1:
        return 7
    return 0
