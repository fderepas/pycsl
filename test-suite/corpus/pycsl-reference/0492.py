"""Test 0492 — strings: str.endswith with a content witness (Stage 3).

`s.endswith(q)` lowers to `val str_endswith_op (s suffix : string) : int` whose `ensures`
relates `result = 1` to `String.substring s (len s - len q) (len q) = q`. Given the suffix
matches at the tail, the method provably returns 1. Counterpart of 0491 (startswith)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(q) <= \str_length(s)
#@ requires \str_sub(s, \str_length(s) - \str_length(q), \str_length(s)) == q
#@ ensures \result == 1
def must_end(s: str, q: str) -> int:
    if s.endswith(q):
        return 1
    return 0
