r"""G29 CG-S5 — route #154 carrier: the element store goes through a LOCAL ALIAS of the field."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]
        xs = self.xs
        xs[0] = 9


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
