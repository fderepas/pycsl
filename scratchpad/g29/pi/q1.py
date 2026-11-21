r"""G29 Q1 — route #150 draft carrier: an INHERITED `__post_init__` (derived @dataclass has none)."""
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class A:
    x: int

    def __post_init__(self) -> None:
        self.x = 7

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


@dataclass
class B(A):
    y: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    b = B(1)
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
