r"""Test 1444 - ROUTE #147: a class that declares NO `__init__` INHERITS the first one in its MRO, and the model gave it an EMPTY `init_params` - so `_call_record_constructor`'s guard `(init_params or kwonly_params)` was FALSE, nothing bound, and every field took `_field_default`'s DEFINITE literal. A PLAIN (undecorated) subclass of a `@dataclass`: `Cee(7).get() == 0` PROVED while CPython returns 7. The inherited field is read through an INHERITED METHOD because a DIRECT base-field read emits the unmangled name and type-errors.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Ay:
    afld: int

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Cee(Ay):
    pass


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
