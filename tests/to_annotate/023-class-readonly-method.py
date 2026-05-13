# Level 1 feature: pure read-only method (no self mutation) — obj_* fields as plain params, no ref

class Scaler:
    def __init__(self, base, factor):
        self._base = base
        self._factor = factor

    def apply(self):
        return self._base * self._factor

    def shift(self, offset):
        self._base = self._base + offset
        return self._base
