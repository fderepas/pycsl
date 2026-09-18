r"""G29 FR2-2 — `assigns \nothing` method mutates a list field through a local alias."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0, 0]

    #@ assigns \nothing
    def poke(self) -> None:
        ys = self.xs
        ys[0] = 5

    #@ ensures \result == 0
    def run(self) -> int:
        b = self.xs[0]
        self.poke()
        return self.xs[0] - b


if __name__ == "__main__":
    print("CPython:", C().run())
