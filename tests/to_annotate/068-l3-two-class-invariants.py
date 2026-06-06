# Level 3 feature: two classes with independent invariants
# Tests: each class gets its own invariant, methods must guard independently

class Temperature:
    def __init__(self):
        self._celsius = 0

    def set_celsius(self, c):
        self._celsius = c
        return self._celsius

    def warm(self, delta):
        self._celsius += delta
        return self._celsius


class Pressure:
    def __init__(self):
        self._pascal = 0

    def set_pascal(self, p):
        self._pascal = p
        return self._pascal

    def increase(self, delta):
        self._pascal += delta
        return self._pascal
