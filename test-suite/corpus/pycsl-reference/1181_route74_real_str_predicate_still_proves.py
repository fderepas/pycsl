"""1181 — ROUTE #74 POSITIVE CONTROL: a REAL str predicate is untouched.

The repair must narrow the oracle to the shadowing case ONLY. On a genuine `str` receiver
the 0/1 model is correct and load-bearing, and `s.isdigit()` must still discharge `<= 1`.
Without this control the fix could be a blanket removal of the predicate model and 1178
would pass for the wrong reason.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result <= 1
#@ assigns \nothing
def f(s: str) -> int:
    return s.isdigit()
