# Level 3 feature: compound upper-bound invariant
# Tests: #@ class invariant 0 <= self._val and self._val <= 100
# A clamped value that is always in [0, 100]

class Clamped:
    def __init__(self):
        self._val = 0

    def set(self, v):
        if v < 0:
            self._val = 0
        elif v > 100:
            self._val = 100
        else:
            self._val = v
        return self._val

    def get(self):
        return self._val
