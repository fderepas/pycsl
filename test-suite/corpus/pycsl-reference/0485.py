"""Test 0485 — strings: __hash__ (`hash(s)`).
Target: hashing a string yields an int (usable as a dict/set key). PROVES as of the G2 strings
feature: `hash(s)` of a string routes to the abstract `val str_hash_op (s:string):int` (an
uninterpreted string→int over a real Why3 string, no int-coercion of the value)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures True
#@ assigns \nothing
def shash(s: str) -> int:
    return hash(s)
