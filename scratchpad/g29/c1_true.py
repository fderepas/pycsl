r"""G29 C1 TRUE TWIN — carrier-rerun on route #147 draft 4: a FOREIGN base (not in `records`) that
DEFINES a constructor sits before the in-module definer in the MRO; the walk `continue`s past it."""
_ = 0  # anchor


class Ay:
    afld: int = 5

    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Cee(Exception, Ay):
    pass


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()


if __name__ == "__main__":
    print("CPython:", probe())
