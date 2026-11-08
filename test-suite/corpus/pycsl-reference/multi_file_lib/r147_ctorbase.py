"""r147_ctorbase — a base class with an explicit positional `__init__`, imported by
witness 1456 so route #147's inherited-constructor copy is exercised ACROSS MODULES.

`Ay` is the class that OWNS the constructor; the importing module derives an undecorated
subclass that declares no `__init__` of its own, so Python gives it `Ay.__init__` verbatim.
"""
_ = 0  # anchor


class Ay:
    afld: int

    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld
