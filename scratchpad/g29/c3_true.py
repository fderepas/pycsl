r"""G29 C3 — carrier-rerun on route #147/#144: `@dataclass(init=False)` on a derived class
generates NO `__init__`, so Python inherits the base's; the decorated arm is #144's SYNTHESIZE."""
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class Ay:
    afld: int

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
