"""synth-003 — CC.5 byte-diff real-corpus case.

Simple subset: subscript read + augmented assignment with multiplication.
"""
_ = 0  # anchor


#@ requires \length(arr) >= 1
#@ ensures True
def synth_003(arr: list, k: int) -> int:
    z = arr[0]
    z *= k
    z -= 3
    return z
