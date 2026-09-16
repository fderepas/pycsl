r"""G29 C8 — C7 with the stateless base NAMED `ABC`: a STATELESS in-module base (no fields, so no `records` entry) defining a
constructor sits before the definer in the MRO."""
_ = 0  # anchor


class ABC:
    def __init__(self, afld: int) -> None:
        pass


class Ay:
    afld: int = 5

    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Cee(ABC, Ay):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()


if __name__ == "__main__":
    print("CPython:", probe())
