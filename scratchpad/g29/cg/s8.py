r"""G29 CG-S8 — route #154 control: a NON-ESCAPING read of the list field in `__init__` (`len(self.xs)`) keeps the literal."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]
        if len(self.xs) > 5:
            pass


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
