r"""del attribute then hasattr"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 1


#@ ensures \result == True
def probe() -> bool:
    c = C()
    del c.x
    return hasattr(c, "x")


if __name__ == "__main__":
    print("CPython:", probe())
