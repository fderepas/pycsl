"""Test 0125 — PyCSL Annotation Reference 3.4.4 (variation B)"""
""  # pycsl
#@ class invariant self._count >= 0
class Tally:
    def __init__(self):
        self._count = 0

    #@ ensures self._count == \old(self._count) + 1
    #@ assigns self._count
    def tick(self) -> int:
        self._count = self._count + 1
        return self._count

if __name__ == "__main__":
    t = Tally()
    assert t.tick() == 1
    assert t.tick() == 2
