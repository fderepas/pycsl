"""synth-004 — CC.5 byte-diff real-corpus case.

Simple subset: chained additions including a length read.
"""
_ = 0  # anchor


#@ requires \length(arr) >= 0
#@ ensures \result >= 0
def synth_004(arr: list, x: int) -> int:
    n = len(arr)
    y = n + x
    return y
