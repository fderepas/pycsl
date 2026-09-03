from typing import List

@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs: List[int] = []

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def add(self) -> None:
        self.xs.append(1)

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def run(self) -> int:
        self.add()
        return len(self.xs)
