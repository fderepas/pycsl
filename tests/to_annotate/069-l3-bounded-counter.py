# Level 3 feature: bounded counter with upper/lower limits
# Tests: cross-field invariant with _min <= _value <= _max

class BoundedCounter:
    def __init__(self):
        self._value = 0
        self._min = 0
        self._max = 100

    def increment(self):
        if self._value < self._max:
            self._value += 1
        return self._value

    def decrement(self):
        if self._value > self._min:
            self._value -= 1
        return self._value

    def get_value(self):
        return self._value

    def get_range(self):
        return self._max - self._min
