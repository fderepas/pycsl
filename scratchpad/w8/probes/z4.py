from typing import List

@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs: List[int] = [0, 7]

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def go(self) -> None:
        self.xs.pop(0)

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def run(self) -> int:
        self.go()
        return self.xs[0]
