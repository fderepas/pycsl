# pure_lib/enm — pure-Python enum module
# Modelled: IntEnum as int with name, auto as counter.


class IntEnum:
    def __init__(self, value, name):
        self._value = value
        self._name = name

    #@ ensures \result == self._value
    def value(self) -> int:
        return self._value

    #@ ensures \result == self._name
    def name(self) -> int:
        return self._name


class AutoCounter:
    def __init__(self):
        self._next = 1

    #@ ensures \result >= 1
    #@ ensures self._next == \result + 1
    def auto(self) -> int:
        v = self._next
        self._next = self._next + 1
        return v


_auto_counter = AutoCounter()


#@ ensures \result >= 1
def auto() -> int:
    return _auto_counter.auto()
