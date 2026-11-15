r"""Test 10008 -- lvT generator-as-seq CONTROL (expected PASS): a terminating tokenizer-shaped
generator (an index loop with a variant, `s[i]` guarded by the loop test, so `no_exception \all`
holds) consumed by a `for` over the list of its yields. Twins: 10001-10007.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import Iterator, List


#@ requires True
#@ ensures True
#@ assigns \nothing
#@ no_exception \all
def chars(s: str) -> Iterator[str]:
    i = 0
    n = len(s)
    #@ loop invariant 0 <= i
    #@ loop variant n - i
    while i < n:
        yield s[i]
        i += 1


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def count(s: str) -> int:
    k = 0
    #@ loop invariant k >= 0
    for c in chars(s):
        k += 1
    return k


if __name__ == "__main__":
    for s in ["", "ab", "xyz"]:
        r = count(s)
        print("VIOLATION contract" if r < 0 else "result", r)
