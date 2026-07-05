"""CAL good — (-7)//2 == -4 in BOTH Python and Euclidean (positive divisor). Must PROVE
(guards against a detector that over-flags all `//`)."""
_ = 0
#@ ensures \result == -4
def f() -> int:
    return (-7) // 2
