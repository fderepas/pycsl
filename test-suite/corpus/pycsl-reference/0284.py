"""Test 0284 — Negative: bare variable in class invariant (semantic error E5)"""
# pycsl-expected: FAIL

""  # pycsl
#@ class invariant self._value >= 0 and max_allowed > 0
class BadClass:
    def __init__(self):
        self._value = 0

    #@ ensures \result == self._value
    #@ assigns \nothing
    def get_value(self) -> int:
        return self._value

if __name__ == "__main__":
    print("PASS")
