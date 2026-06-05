"""Test 0514 — string + dict: substring-containment witness drives a Counter.

Combines the string `in` containment witness (a known prefix occurrence proves `needle in
haystack`) with the Counter/dict increment model: on a match, `c[0] += 1`, so from the empty
counter the result is 1."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import Counter


#@ requires \str_length(needle) <= \str_length(haystack)
#@ requires \str_sub(haystack, 0, \str_length(needle)) == needle
#@ ensures \result == 1
def count_match(haystack: str, needle: str) -> int:
    c = Counter()
    if needle in haystack:
        c[0] += 1
    return c[0]
