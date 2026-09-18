r"""hasattr on a missing attribute"""
from typing import List, Dict, Any
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v = 0


#@ ensures \result == True
def probe() -> bool:
    c = C()
    return hasattr(c, "w")


if __name__ == "__main__":
    print("CPython:", probe())
