r"""G29 DC5 — #151 x #144: a BASE dataclass's `field(init=False)` field is not in the DERIVED signature."""
from dataclasses import dataclass, field
_ = 0  # anchor


@dataclass
class A:
    y: int = field(init=False, default=5)

    #@ requires True
    #@ ensures \result == self.y
    def gety(self) -> int:
        return self.y


@dataclass
class B(A):
    x: int = 0


#@ ensures \result == 3
#@ assigns \nothing
def probe() -> int:
    b = B(3)
    return b.gety()


if __name__ == "__main__":
    print("CPython:", probe())
