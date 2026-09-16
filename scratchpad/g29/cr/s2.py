r"""G29 S2 — route #149 family: an omitted Optional parameter default read through `is None`."""
from typing import Optional
_ = 0  # anchor


class Cy:
    def __init__(self, k: Optional[int] = 7) -> None:
        self.k = k


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.k is None:
        return 0
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
