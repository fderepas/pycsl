"""Test 0489 — strings: __iter__ / character iteration (counting yields the length).
Target: iterating a string visits each character once; counting yields its length. PROVES as of
the G2 strings feature: a string is a real Why3 `string`, `len(s)` is `String.length s`. The
canonical PyCSL loop form is an explicit index `i` advancing to `\str_length(s)`. (The `for c in
s` form lowers to the same `str_length_op`/`str_sub_op` bridges via `_classify_iterable`, but the
index it walks is internal and not source-referenceable, so the counting postcondition — which
must relate `count` to the iteration index — is stated over an explicit `i` here.)"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == \str_length(s)
#@ assigns \nothing
def count_iter(s: str) -> int:
    count = 0
    i = 0
    #@ loop invariant 0 <= i and i <= \str_length(s)
    #@ loop invariant count == i
    #@ loop variant \str_length(s) - i
    while i < len(s):
        count = count + 1
        i = i + 1
    return count
