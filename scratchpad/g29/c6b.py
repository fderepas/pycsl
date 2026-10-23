r"""G29 C6 — carrier-rerun on route #147's `not _is_dataclass_decorated` exclusion: a
`@dataclass(init=False)` subclass of a PLAIN class with an explicit `__init__`. The decorator
generates NO constructor, so Python inherits `Ay.__init__`; #147 skips every decorated class."""
from dataclasses import dataclass
_ = 0  # anchor


class Ay:
    afld: int

    def __init__(self, afld: int) -> None:
        self.afld = afld + 100

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


@dataclass(init=False)
class Cee(Ay):
    cfld: int = 3


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()


if __name__ == "__main__":
    print("CPython:", probe())
