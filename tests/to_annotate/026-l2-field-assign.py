# Level 2 feature: FieldAssign (plain self.x = v, not +=)
# Tests FieldAssign IR node → self._val <- v in WhyML

class Register:
    def __init__(self):
        self._val = 0

    def set(self, v):
        self._val = v
        return self._val

    def get(self):
        return self._val
