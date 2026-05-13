# Level 2 feature: multi-field record type
# Tests type_decls with two mutable fields { mutable _lo: int; mutable _hi: int }

class Range:
    def __init__(self, lo, hi):
        self._lo = lo
        self._hi = hi

    def widen(self, delta):
        self._lo -= delta
        self._hi += delta

    def size(self):
        return self._hi - self._lo
