# Level 3 feature: capacity constraint invariant
# Tests: #@ class invariant self._size <= self._capacity
# A fixed-capacity buffer; push is guarded by capacity

class Buffer:
    def __init__(self):
        self._size = 0
        self._capacity = 10

    def push(self, n):
        if self._size < self._capacity:
            self._size += 1
        return self._size

    def clear(self):
        self._size = 0
        return self._size

    def free(self):
        return self._capacity - self._size
