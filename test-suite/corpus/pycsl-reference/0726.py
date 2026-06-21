"""Test 0726 — HAPPY H-D: totality / availability (positive).

`#@ happy availability: targets parse total` (macsl's `\context(\total)`) names the
totality guarantee: an attacker-controlled input must not cause non-termination. PyCSL
functions are total by DEFAULT — Why3 emits a termination VC and each loop needs a
`#@ loop variant` — so the bounded parse loop (variant `n - i`) is proved to terminate and
the file verifies. (`no_exception \all` covers the complementary no-uncaught-exception half;
included here so the function is total in the full sense.)
"""
# pycsl-flags: --memory-model hoare
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ requires n >= 0
    #@ no_exception \all
    #@ ensures \result >= 0
    def parse(self, n: int) -> int:
        i: int = 0
        acc: int = 0
        #@ loop invariant 0 <= i and i <= n
        #@ loop invariant acc >= 0
        #@ loop variant n - i
        while i < n:
            acc = acc + 1
            i = i + 1
        return acc
