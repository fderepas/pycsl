# pure_lib/coll — pure-Python collections module
# Modelled: defaultdict (dict with default factory) and deque (circular buffer).


class defaultdict:
    def __init__(self, default_factory):
        self._factory = default_factory
        self._keys = []
        self._vals = []
        self._size = 0

    #@ ensures \result >= 0
    def _find(self, key) -> int:
        i = 0
        #@ loop invariant 0 <= i
        #@ loop invariant i <= self._size
        #@ loop variant self._size - i
        while i < self._size:
            if self._keys[i] == key:
                return i
            i = i + 1
        return -1

    def __getitem__(self, key):
        idx = self._find(key)
        if idx >= 0:
            return self._vals[idx]
        val = self._factory()
        self._keys.append(key)
        self._vals.append(val)
        self._size = self._size + 1
        return val

    def __setitem__(self, key, val):
        idx = self._find(key)
        if idx >= 0:
            self._vals[idx] = val
        else:
            self._keys.append(key)
            self._vals.append(val)
            self._size = self._size + 1

    def __contains__(self, key):
        return self._find(key) >= 0


#@ class invariant self._size >= 0
#@ class invariant self._cap > 0
class deque:
    def __init__(self):
        self._data = [0] * 16
        self._cap = 16
        self._head = 0
        self._size = 0

    #@ ensures \result == self._size
    def __len__(self) -> int:
        return self._size

    def _grow(self):
        new_cap = self._cap * 2
        new_data = [0] * new_cap
        i = 0
        #@ loop invariant 0 <= i
        #@ loop invariant i <= self._size
        #@ loop variant self._size - i
        while i < self._size:
            idx = (self._head + i) % self._cap
            new_data[i] = self._data[idx]
            i = i + 1
        self._data = new_data
        self._head = 0
        self._cap = new_cap

    def append(self, x):
        if self._size == self._cap:
            self._grow()
        idx = (self._head + self._size) % self._cap
        self._data[idx] = x
        self._size = self._size + 1

    def appendleft(self, x):
        if self._size == self._cap:
            self._grow()
        self._head = (self._head - 1) % self._cap
        self._data[self._head] = x
        self._size = self._size + 1

    #@ requires self._size > 0
    def pop(self):
        self._size = self._size - 1
        idx = (self._head + self._size) % self._cap
        return self._data[idx]

    #@ requires self._size > 0
    def popleft(self):
        val = self._data[self._head]
        self._head = (self._head + 1) % self._cap
        self._size = self._size - 1
        return val
