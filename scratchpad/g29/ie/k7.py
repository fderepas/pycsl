r"""missing key via method on self dict, caught in caller"""
from typing import Dict, List, Set
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    def get(self) -> int:
        return self.d["b"]


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        v = c.get()
    except KeyError:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
