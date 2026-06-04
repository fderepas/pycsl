"""Test 0478 — strings-plan demand-driver: __le__ (`s <= t`, lexicographic).
Target: lexicographic comparison. NOTE this is a STRETCH target — the planned `s[i]`-as-
1-char-substring model has no code points, so character ordering may remain unsupported even
after the core string feature (see strings-plan.md risks). Expected-FAIL."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def le(s: str, t: str) -> bool:
    return s <= t
