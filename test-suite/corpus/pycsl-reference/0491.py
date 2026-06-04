"""Test 0491 — strings: str.startswith with a content witness (Stage 3).

`s.startswith(p)` on a simple `str` receiver lowers to `val str_startswith_op (s prefix :
string) : int` whose `ensures` keeps the 0/1 result AND relates `result = 1` to the
substring condition `String.substring s 0 (String.length p) = p`. So given the prefix
actually matches, the method provably returns 1 (the receiver is lifted to an operand;
chained / non-`str` receivers keep the opaque predicate model — see 0453)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(p) <= \str_length(s)
#@ requires \str_sub(s, 0, \str_length(p)) == p
#@ ensures \result == 1
def must_start(s: str, p: str) -> int:
    if s.startswith(p):
        return 1
    return 0
