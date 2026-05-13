# Level 3 feature: class invariant alongside a standalone function
# Tests that the invariant applies only to the class, not the function

class Tally:
    def __init__(self):
        self._count = 0

    def tick(self):
        self._count += 1
        return self._count

    def get(self):
        return self._count


def double(n):
    return n * 2
