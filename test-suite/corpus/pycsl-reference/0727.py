"""Test 0727 — negative: a `total` target marked `\diverges` is rejected (H-D).

The `availability` policy claims `parse` is total, but `parse` also declares `#@ \diverges`
(it opts OUT of termination). The meta-pass rejects this contradiction as a hard error.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ requires n >= 0
    #@ \diverges
    #@ ensures \result >= 0
    def parse(self, n: int) -> int:
        i: int = 0
        acc: int = 0
        #@ loop invariant 0 <= i and i <= n
        while i < n:
            acc = acc + 1
            i = i + 1
        return acc
