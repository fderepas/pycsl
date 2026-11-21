r"""Test 5700 -- R5-str (int-erasure-seam-r3-impl.md): a whole-list `s.split(sep)` on a `str`
receiver outside `@mutable_state` is the receiver-passing `str_split_op : array string`, and an
element read `lines[i].strip() == qn` is the faithful `str_eq_op (str_strip_op lines[i]) qn`
(was `s_split_1 <hash>` + `strip_1 (subscript_get ...)`, an L3-tc clash). Positive control.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures 0 <= \result
#@ assigns \nothing
def count_split(stdout: str, qn: str) -> int:
    lines = stdout.split("\n")
    n = 0
    i = 0
    #@ loop invariant 0 <= i <= len(lines)
    #@ loop invariant 0 <= n <= i
    #@ loop variant len(lines) - i
    while i < len(lines):
        if lines[i].strip() == qn:
            n = n + 1
        i = i + 1
    return n
