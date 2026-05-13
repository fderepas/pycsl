# Level 3 feature: invariant preserved across many mutating methods
# Tests that Why3 checks the invariant at every method boundary

class Score:
    def __init__(self):
        self._points = 0

    def add(self, n):
        self._points += n
        return self._points

    def subtract(self, n):
        if self._points >= n:
            self._points -= n
        return self._points

    def reset(self):
        self._points = 0
        return self._points

    def get(self):
        return self._points
