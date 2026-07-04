"""Test 0793 — NEGATIVE: case folding is NOT unconditionally length-preserving.

cleared-string RESIDUALS item 1 negative gate. Python `str.upper()` uses FULL
Unicode case folding, which is NOT length-preserving (`"ß".upper() == "SS"` grows).
So the abstract `str_upper_op` carries ONLY a non-emptiness length law — never a
length-EQUALITY law. This driver FALSELY claims `len(s.upper()) == len(s)`; the
model is honest and must NOT prove it, so this is expected to FAIL. It guards the
case model against silently regaining an unsound length-preservation claim.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires len(s) >= 1
#@ ensures len(\result) == len(s)
#@ assigns \nothing
def upper_len_false(s: str) -> str:
    return s.upper()
