"""v43 AGREE — ROUTE #85's completeness gain. The dict literal now reaches the allocation site
as the same `map_update_some` chain a LOCAL dict literal always got, so the TRUE value is
provable where the model previously insisted the map was empty. CPython returns 5."""
from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.d.get(1, 0)


if __name__ == "__main__":
    print(f())
