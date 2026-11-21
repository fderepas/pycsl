r"""G29 C2 — carrier-rerun on route #147 draft 4: `__init__` bound in the class body by an
ASSIGNMENT, not a `def`, so `_own147` is False and the class is marked `init_inherits`."""
_ = 0  # anchor


class Ay:
    afld: int

    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


def _mk(self: "Ay", afld: int) -> None:
    self.afld = afld + 100


class Cee(Ay):
    __init__ = _mk


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()


if __name__ == "__main__":
    print("CPython:", probe())
