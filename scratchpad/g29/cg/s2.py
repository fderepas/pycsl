r"""G29 CG-S2 — `__init__` writes a KEY of a dict field it just initialised."""
from typing import Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.d: Dict[int, int] = {1: 5}
        self.d[1] = 9


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.d[1]


if __name__ == "__main__":
    print("CPython:", probe())
