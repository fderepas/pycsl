r"""Test 1760 — WITNESS: `#@ footprint` naming a parametric policy that does not exist.

A footprint binds a method to a NAMED parametric `happy` policy. A name that matches no
policy would bind the method to nothing while looking like a binding — so it is refused,
and until now nothing proved that. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy inode_conf(n):
#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]
#@     except formatter
#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024


d = Disk()


#@ requires 0 <= k and k < 8
#@ footprint nosuchpolicy(k)
#@ assigns d.disk
def writer(k: int, v: int) -> None:
    d.disk[512 + k * 64] = v


#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0
