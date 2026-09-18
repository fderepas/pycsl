r"""module constant dict mutated in a class body"""
from typing import List, Dict
_ = 0  # anchor


OP: Dict[str, int] = {"a": 1}


class C:
    OP["a"] = 9

    def __init__(self) -> None:
        self.k = 0


#@ ensures \result == 1
def probe() -> int:
    return OP["a"]


if __name__ == "__main__":
    print("CPython:", probe())
