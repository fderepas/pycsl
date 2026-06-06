"""synth-001 — CC.5 byte-diff real-corpus case.

Simple subset: two assignments with integer literals and a binop.
Body excludes the trailing return per the bytediff convention.
"""
_ = 0  # anchor


#@ requires True
#@ ensures \result == x + 1
def synth_001(x: int) -> int:
    z = 0
    z = x + 1
    return z
