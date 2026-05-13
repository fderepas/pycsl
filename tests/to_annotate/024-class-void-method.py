# Level 1 feature: void method (no return statement) — tests unit return type path in Module6

class Clamp:
    def __init__(self, min_val, max_val):
        self._value = 0
        self._min = min_val
        self._max = max_val

    def set_value(self, v):
        if v < self._min:
            self._value = self._min
        else:
            if v > self._max:
                self._value = self._max
            else:
                self._value = v

    def get_value(self):
        return self._value
