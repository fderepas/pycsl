"""S5 STATIC gate — G4: bound is an instantiation-time obligation.

Per the two-plane spec §1.3: `C[T: int]` instantiated with `int` is admissible
(G4 pass); instantiated with `str` is REJECTED (invariant checking per GT2).
This driver is the PASS case (int).
"""
_ = 0
class C[T: int]:
    def __init__(self):
        self._v = 0

if __name__ == "__main__":
    c = C[int]()
