"""Test 0486 — strings: __str__ (`str(s)`).
Target: str() of a str is the same string (identity). PROVES as of the G2 strings feature:
`str(s)` on a string-typed arg returns the argument unchanged (the identity, mirroring the
existing int identity), so `\result == s` holds definitionally."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == s
#@ assigns \nothing
def tostr(s: str) -> str:
    return str(s)
