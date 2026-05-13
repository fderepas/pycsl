# Level 3 feature: monotone accumulator with invariant
# Tests: #@ class invariant self._total >= 0 on a class that only adds

class Accumulator:
    def __init__(self):
        self._total = 0

    def add(self, n):
        self._total += n
        return self._total

    def value(self):
        return self._total
