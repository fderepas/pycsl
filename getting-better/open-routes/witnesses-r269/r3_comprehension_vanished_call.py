from typing import List
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    def spin(self, k: int) -> int:
        while k > 0:
            k = k + 1
        return 0

    #@ ensures \result == 7
    #@ assigns \nothing
    def m(self, xs: List[int]) -> int:
        ys = [self.spin(x) for x in xs]
        return 7
