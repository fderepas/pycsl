"""Test 0493 — strings: str.find with a found-index witness (Stage 3).

`s.find(sub)` lowers to `val str_find_op (s sub : string) : int` whose `ensures` give
`result >= -1` and, when `result >= 0`, the witness that `sub` occurs at that index:
`String.substring s result (String.length sub) = sub` (with the index in range). A caller can
therefore use the returned index to slice out a guaranteed-matching occurrence — the same
content reasoning the flagship search driver 0471 establishes for the hand-written loop."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(sub) >= 1
#@ ensures \result >= -1
#@ ensures \result >= 0 ==> \result + \str_length(sub) <= \str_length(s)
#@ ensures \result >= 0 ==> \str_sub(s, \result, \result + \str_length(sub)) == sub
#@ assigns \nothing
def locate(s: str, sub: str) -> int:
    return s.find(sub)
