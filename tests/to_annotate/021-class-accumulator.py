# Level 1 feature: single mutable field, basic += mutation, return value from method

class RunningSum:
    def __init__(self):
        self._total = 0

    def add(self, amount):
        self._total += amount
        return self._total

    def reset(self):
        self._total = 0
        return self._total
