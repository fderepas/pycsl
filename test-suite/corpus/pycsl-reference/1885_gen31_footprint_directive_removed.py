r"""Test 1885 — gen #31 CONTROL for 1884 (expected PASS): without the directive it verifies.

Byte-identical to 1884 with the `#@ footprint` line removed. The refusal is about a NAME
that resolves to nothing, not about the file — the same control discipline routes #13 and
#223 pay for. If this one ever goes red, the hoisted validation has started refusing
something other than the typo it was written for.
"""# pycsl-expected: PASS
_ = 0  # anchor


#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024


d = Disk()


#@ assigns d.disk
def writer(v: int) -> None:
    d.disk[0] = v
