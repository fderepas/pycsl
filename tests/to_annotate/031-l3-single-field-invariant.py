# Level 3 feature: single-field class invariant
# Tests: #@ class invariant self._n >= 0 on a counter with increment/reset

class Counter:
    def __init__(self):
        self._n = 0

    def increment(self, amount):
        self._n += amount
        return self._n

    def reset(self):
        self._n = 0
        return self._n
