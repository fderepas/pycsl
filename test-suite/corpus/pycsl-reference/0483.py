"""Test 0483 — strings: __rmul__ (`n * s`, reflected repetition).
Target: integer-on-the-left repetition. Same semantics as __mul__. PROVES as of the G2 strings
feature: the int×string `*` canonicalizes string-first and lowers to the same `str_repeat_op`
whose `ensures` pins `String.length result = n * String.length s`."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires n >= 0 and \str_length(s) >= 0
#@ ensures \str_length(\result) == n * \str_length(s)
#@ assigns \nothing
def rrep(n: int, s: str) -> str:
    return n * s
