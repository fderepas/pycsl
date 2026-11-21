r"""Test 2825 — route #266 (expected FAIL): the READ-confinement form checked only reads spelled
`self.secret[i]`, so a non-exempt method reading ANOTHER instance's confined cell, `o.secret[1]`
(inside the region [0, 4)), was PROVED confined. CPython: 7 (the confined cell). Now refused:
a read through a receiver other than `self` is not covered by the per-read-site check.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy conf:
#@     region 0 .. 4
#@     reads self.secret outside region
#@     except reader
#@ class invariant \length(self.secret) >= 8
class S:
    def __init__(self) -> None:
        self.secret: list[int] = [7] * 8

    #@ assigns \nothing
    def reader(self) -> int:
        return self.secret[0]

    #@ assigns \nothing
    def peeker(self, o: "S") -> int:
        return o.secret[1]

if __name__ == "__main__":
    print(S().peeker(S()))
