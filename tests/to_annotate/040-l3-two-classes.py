# Level 3 feature: two classes, each with its own class invariant
# Tests that multiple type_decls each carry independent invariants

class Up:
    def __init__(self):
        self._x = 0

    def inc(self, n):
        self._x += n
        return self._x

    def get(self):
        return self._x


class Down:
    def __init__(self):
        self._y = 100

    def dec(self, n):
        self._y -= n
        return self._y

    def get(self):
        return self._y
