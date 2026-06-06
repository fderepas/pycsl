"""synth-005 — CC.5 byte-diff: comparison in expression position.

Exercises the ECmp constructor. The result of `x < 10` is stored in
an integer variable as 0 or 1 (Python's bool ↔ int interop).
"""
_ = 0  # anchor


#@ requires True
#@ ensures True
def synth_005(x: int) -> int:
    flag = x < 10
    return flag
