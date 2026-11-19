"""Test 1256 — route #93 CONTROL: the guard is scoped to the TARGET, not to the file.

The route #93 repair rejects `\trusted` / `\abstract` on a `total` policy's TARGET. It must not
reject a `\trusted` function that merely shares the file. Here `parse` is the target and has a
verified, variant-carrying loop (so the termination VC discharges), while `helper` is
`\trusted` and is NOT the target — and the file VERIFIES.

Without this control, "1254 and 1255 are rejected" would be consistent with the repair having
banned `\trusted` from any module carrying a `total` policy, which would be a narrowing far
beyond the measured defect. This is the anti-over-narrowing control corpus 1057 taught the
campaign to write, and it fails if the guard is ever widened from `target_fns` to all `funcs`.
"""
# pycsl-flags: --memory-model hoare
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ \trusted reviewer: demo
    #@ requires n >= 0
    #@ ensures \result >= 0
    def helper(self, n: int) -> int:
        return n

    #@ requires n >= 0
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
