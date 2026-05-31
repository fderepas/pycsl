"""PyCSL mock for Python's collections module.

Provides trusted stubs for specialized container datatypes.
"""
_ = 0  # anchor

# ── namedtuple factory ──────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.namedtuple
#@ requires name >= 0
#@ ensures \result >= 0
def namedtuple(name: int, fields: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.somenamedtuple._make
#@ requires True
#@ ensures True
def namedtuple__make(iterable: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
def namedtuple__asdict(self: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
def namedtuple__replace(self: int, kwargs: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.somenamedtuple._fields
#@ requires True
#@ ensures True
def namedtuple__fields(self: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.somenamedtuple._field_defaults
#@ requires True
#@ ensures True
def namedtuple__field_defaults(self: int) -> int:
    return 0

# ── DequeObj class ──────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._size >= 0
#@ class invariant self._maxlen >= -1
class DequeObj:
    def __init__(self):
        self._size = 0
        self._maxlen = -1

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def append(self, item: int) -> int:
        self._size += 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def appendleft(self, item: int) -> int:
        self._size += 1
        return 0

    #@ \trusted
    #@ requires self._size >= 1
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def pop(self) -> int:
        self._size -= 1
        return 0

    #@ \trusted
    #@ requires self._size >= 1
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def popleft(self) -> int:
        self._size -= 1
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.deque.extend
#@ requires True
#@ ensures True
#@ assigns self._size
    def extend(self, iterable: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.deque.extendleft
#@ requires True
#@ ensures True
#@ assigns self._size
    def extendleft(self, iterable: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.deque.rotate
#@ requires True
#@ ensures True
#@ assigns self
    def rotate(self, n: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._size == 0
    #@ assigns self._size
    def clear(self) -> int:
        self._size = 0
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.deque
#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
    def count(self, value: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/stdtypes.html#common-sequence-operations
#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
    def index(self, value: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
#@ assigns self._size
    def insert(self, idx: int, value: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.deque.remove
#@ requires True
#@ ensures True
    def remove(self, value: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.deque.reverse
#@ requires True
#@ ensures True
#@ assigns \nothing
    def reverse(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.copy.html
#@ requires True
#@ ensures True
#@ assigns \nothing
    def copy(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._maxlen
    #@ assigns \nothing
    def maxlen_val(self) -> int:
        return self._maxlen

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._size
    #@ assigns \nothing
    def size(self) -> int:
        return self._size

# ── CounterObj class ────────────────────────────────────────────────

#@ class invariant self._total >= 0
class CounterObj:
    def __init__(self):
        self._total = 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.Counter.elements
#@ requires True
#@ ensures True
#@ assigns \nothing
    def elements(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.Counter.most_common
#@ requires n >= 0
#@ ensures True
#@ assigns \nothing
    def most_common(self, n: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
#@ assigns self._total
    def subtract(self, iterable: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.Counter.update
#@ requires True
#@ ensures True
#@ assigns self._total
    def update(self, iterable: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._total
    #@ assigns \nothing
    def total_count(self) -> int:
        return self._total

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._total == 0
    #@ assigns self._total
    def clear(self) -> int:
        self._total = 0
        return 0

# ── OrderedDictObj class ────────────────────────────────────────────

#@ class invariant self._od_count >= 0
class OrderedDictObj:
    def __init__(self):
        self._od_count = 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.OrderedDict.move_to_end
#@ requires True
#@ ensures True
#@ assigns self
    def move_to_end(self, key: int, last: int) -> int:
        return 0

    #@ \trusted
    #@ requires self._od_count >= 1
    #@ ensures self._od_count == \old(self._od_count) - 1
    #@ assigns self._od_count
    def popitem(self, last: int) -> int:
        self._od_count -= 1
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def get_item(self, key: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
    def set_item(self, key: int, value: int) -> int:
        return 0

    #@ \trusted
    #@ requires self._od_count >= 1
    #@ ensures self._od_count == \old(self._od_count) - 1
    #@ assigns self._od_count
    def del_item(self, key: int) -> int:
        self._od_count -= 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._od_count
    #@ assigns \nothing
    def size(self) -> int:
        return self._od_count

# ── DefaultDictObj class ───────────────────────────────────────────

#@ class invariant self._dd_count >= 0
class DefaultDictObj:
    def __init__(self):
        self._dd_count = 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.defaultdict.__missing__
#@ requires True
#@ ensures True
#@ assigns self._dd_count
    def missing(self, key: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def get_item(self, key: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
#@ assigns self._dd_count
    def set_item(self, key: int, value: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._dd_count
    #@ assigns \nothing
    def size(self) -> int:
        return self._dd_count

# ── ChainMapObj class ──────────────────────────────────────────────

#@ class invariant self._maps_count >= 1
class ChainMapObj:
    def __init__(self):
        self._maps_count = 1

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def new_child(self, m: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.parents
#@ requires True
#@ ensures True
#@ assigns \nothing
    def parents(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._maps_count
    #@ assigns \nothing
    def maps_count(self) -> int:
        return self._maps_count

# ── UserDict ────────────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
def UserDict(kwargs: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.UserDict
#@ requires True
#@ ensures True
def UserDict_data(self: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
def UserDict_popitem(self: int) -> int:
    return 0

# ── UserList ────────────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.UserList
#@ ensures True
def UserList(lst: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.UserList
#@ requires True
#@ ensures True
def UserList_data(self: int) -> int:
    return 0

# ── UserString ──────────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/collections.html#collections.UserString
#@ requires True
#@ ensures True
def UserString(seq: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
#@ requires True
#@ ensures True
def UserString_data(self: int) -> int:
    return 0
