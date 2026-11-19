from typing import List

_g: List[int] = [0, 7]

#@ requires True
#@ ensures \length(_g) == 2
#@ assigns \nothing
def f() -> None:
    _g.append(9)
