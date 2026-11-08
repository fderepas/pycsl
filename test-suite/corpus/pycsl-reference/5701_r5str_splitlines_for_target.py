r"""Test 5701 -- R5-str: `s.splitlines()` is `str_splitlines_op : array string`; iterating it
binds a real string element, and `for ln in <List[str] param>` types `ln` as a string, so
`ln.strip() == b` is `str_eq_op (str_strip_op !ln) b` (was the input-blind `ln_strip_0 ()`).
Positive control (the counters stay non-negative through both loops).
"""
# pycsl-expected: PASS
from typing import List


#@ ensures 0 <= \result
#@ assigns \nothing
def count_eq(lines: List[str], b: str) -> int:
    n = 0
    #@ loop invariant 0 <= n
    for ln in lines:
        if ln.strip() == b:
            n = n + 1
    return n


#@ ensures 0 <= \result
#@ assigns \nothing
def total_len(s: str) -> int:
    n = 0
    #@ loop invariant 0 <= n
    for q in s.splitlines():
        n = n + len(q)
    return n + len(s.splitlines())
