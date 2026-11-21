r"""Test 1799 — WITNESS: a `\trusted` function whose BODY writes a policy's parametric path.

`happy <p>(<k>)`: a function that is `#@ \trusted` (so its body is NEVER LOWERED), is not
in the `except` set, has no `#@ footprint`, and writes the protected parametric path. The
`#@ check False` the policy would stamp on that write is never proved, so the containment
claim would hold by nothing at all. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy inode_conf(n):
#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]
#@     except formatter
#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024


d = Disk()


#@ \trusted reviewer: witness-only
#@ requires 0 <= k and k < 8
#@ assigns d.disk
def sneaky(k: int, v: int) -> None:
    d.disk[512 + k * 64] = v


#@ assigns d.disk
def formatter(v: int) -> None:
    d.disk[0] = v
