# Level 1 feature: mixed file — standalone function + class in the same module
# Tests that visit_ClassDef resets _current_class so the top-level function is NOT prefixed

def is_positive(n):
    if n > 0:
        return 1
    else:
        return 0


class Accumulator:
    def __init__(self):
        self._total = 0

    def add(self, n):
        self._total += n
        return self._total

    def get(self):
        return self._total
