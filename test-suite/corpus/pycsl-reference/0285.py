"""Test 0285 — Negative: subscript variable in class invariant not a field (semantic error E5)"""
# pycsl-expected: FAIL

""  # pycsl
#@ class invariant self._value >= 0 and limit >= 0
class TypoClass:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    #@ assigns self._value
    def add(self, amount: int) -> int:
        self._value = self._value + amount
        return self._value

if __name__ == "__main__":
    print("PASS")
