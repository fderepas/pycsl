"""Test 0794 — NEGATIVE: general grow replace is NOT length-preserving.

cleared-string RESIDUALS item 2 negative gate. `str_replace_op`'s length law fires
ONLY for the char-for-char case (`len pat == len rep`). Here `pat="a"` (len 1) is
replaced by `"bb"` (len 2), so the result may grow — no sound length law applies.
This driver FALSELY claims `len(s.replace("a","bb")) == len(s)`; the model must NOT
prove it, so this is expected to FAIL. It guards against a false length-preservation
claim leaking into the general grow/shrink replace case.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures len(\result) == len(s)
#@ assigns \nothing
def replace_grow_false(s: str) -> str:
    return s.replace("a", "bb")
