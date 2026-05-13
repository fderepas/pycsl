# Level 1 feature: two mutable fields, cross-field contract (requires self._value < self._max)

class BoundedCounter:
    def __init__(self, maximum):
        self._value = 0
        self._max = maximum

    def increment(self):
        if self._value < self._max:
            self._value += 1
        return self._value

    def get_max(self):
        return self._max
