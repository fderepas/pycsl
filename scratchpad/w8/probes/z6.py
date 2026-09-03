from typing import List

#@ class invariant \length(self.xs) == 2
@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs: List[int] = [0, 7]

    #@ requires True
    #@ ensures \length(self.xs) == 2
    #@ assigns \nothing
    def go(self) -> None:
        self.xs.append(9)
