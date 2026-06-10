"""Test 0484 — strings: __mod__ (`s % x`, old-style formatting).
Target: %-formatting. Content of the result is NOT modeled (opaque) — this documents the
boundary; only that it produces a string. PROVES as of the G2 strings feature: a string-LHS `%`
lowers to the honest abstract `val str_mod_op (s:string)(x:'a):string` whose only `ensures` is
the sound over-approximation `String.length result >= 0` (we never model the formatting)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def fmt(s: str, x: int) -> str:
    return s % x
