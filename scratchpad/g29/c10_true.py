r"""G29 C10 — a CROSS-MODULE diamond: `Bee(Ay)` inherits its constructor in the imported
module; here `Cee(Ay)` defines `afld + 100` and `Dee(Bee, Cee)`. C3: Dee, Bee, Cee, Ay."""
_ = 0  # anchor
from mflib.r147_diamondlib import Ay, Bee


class Cee(Ay):
    def __init__(self, afld: int) -> None:
        self.afld = afld + 100


class Dee(Bee, Cee):
    pass


#@ ensures \result == 107
#@ assigns \nothing
def probe() -> int:
    o = Dee(7)
    return o.get()


if __name__ == "__main__":
    print("CPython:", probe())
