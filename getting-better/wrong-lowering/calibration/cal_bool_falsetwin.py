"""CAL good — the FALSE twin of the bool case must be UNPROVABLE (sound)."""
_ = 0
#@ ensures \result == 2
def f(x: bool) -> int:
    if x:
        return 1
    return 0
