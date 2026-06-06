"""synth-002 — CC.5 byte-diff real-corpus case.

Simple subset: three assignments, augmented assignment.
"""
_ = 0  # anchor


#@ requires True
#@ ensures \result >= 0
def synth_002(x: int, y: int) -> int:
    a = x
    b = y
    a += b
    return a
