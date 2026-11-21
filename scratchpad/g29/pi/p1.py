r"""G29 P1 — `@dataclass` with `__post_init__` overwriting a field: is the hook modelled?"""
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    x: int

    def __post_init__(self) -> None:
        self.x = 7

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    return p.get()


if __name__ == "__main__":
    print("CPython:", probe())
