from typing import List


class W:
    def __init__(self) -> None:
        self.x: int = 0

    #@ ensures \result == 3
    #@ assigns \nothing
    def m(self) -> int:
        def len(xs: List[int]) -> int:
            return 0
        return len([1, 2, 3])


if __name__ == "__main__":
    r = W().m()
    print("VIOLATION m() =", r) if r != 3 else print("no violation")
