# Level 3 feature: cross-field ordering invariant
# Tests: #@ class invariant self._lo <= self._hi
# Two fields that must remain ordered at all times

class Interval:
    def __init__(self):
        self._lo = 0
        self._hi = 0

    def set_lo(self, lo):
        self._lo = lo
        return self._lo

    def set_hi(self, hi):
        self._hi = hi
        return self._hi

    def width(self):
        return self._hi - self._lo
