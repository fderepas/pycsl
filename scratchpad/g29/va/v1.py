r"""G29 VA1 — `__init__(self, **kwargs)` storing `self.x = kwargs.get("x", 3)`."""
from typing import Any
_ = 0  # anchor


class C:
    def __init__(self, **kwargs: int) -> None:
        self.x = kwargs.get("x", 3)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(x=9)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
