"""Test 0728 — negative: an unbounded loop under a `total` policy fails termination (H-D).

`parse`'s loop has NO `#@ loop variant`, so Why3's default termination VC is unprovable —
exactly the non-termination (DoS) the totality policy is meant to exclude.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ requires n >= 0
    #@ ensures \result >= 0
    def parse(self, n: int) -> int:
        i: int = 0
        acc: int = 0
        #@ loop invariant 0 <= i and i <= n
        while i < n:
            acc = acc + 1
            i = i + 1
        return acc
