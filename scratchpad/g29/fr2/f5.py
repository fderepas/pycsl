r"""G29 FR2-5 — method mutates a record held in a list field."""
from typing import List
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 0


class C:
    def __init__(self) -> None:
        self.ps: List[P] = [P()]

    #@ assigns \nothing
    def poke(self) -> None:
        self.ps[0].x = 5

    #@ ensures \result == 0
    def run(self) -> int:
        b = self.ps[0].x
        self.poke()
        return self.ps[0].x - b


if __name__ == "__main__":
    print("CPython:", C().run())
