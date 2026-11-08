from typing import List

@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs: List[int] = [0, 7]

#@ requires \length(c.xs) == 2
#@ ensures \length(c.xs) == 2
#@ assigns \nothing
def f(c: C) -> None:
    c.xs.append(9)
