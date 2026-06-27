"""S5 STATIC gate — G4 reject: bound violation is a loud-fail.

Per the two-plane spec §1.3: `C[T: int]` instantiated with `str` is REJECTED
(invariant checking per GT2). This driver must FAIL with PYCSL-TY3-BOUND.
"""
_ = 0
class C[T: int]:
    def __init__(self):
        self._v = 0

if __name__ == "__main__":
    c = C[str]()
