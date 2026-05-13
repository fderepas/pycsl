# Level 2 feature: pure read-only method (no FieldAssign in body)
# Tests that FieldGet in return expression emits self.field with no <- assignment

class Segment:
    def __init__(self, start, end):
        self._start = start
        self._end = end

    def length(self):
        return self._end - self._start

    def contains(self, point):
        if point >= self._start:
            if point < self._end:
                return 1
            else:
                return 0
        else:
            return 0
