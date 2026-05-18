"""Test 0006 — PyCSL Annotation Reference 2.3.1"""
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    #@ assigns self._value
    def increment(self, amount: int) -> int:
        self._value = self._value + amount
        return self._value

if __name__ == "__main__":
    c = Counter()
    assert c.increment(5) == 5
    assert c.increment(3) == 8
