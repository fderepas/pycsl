r"""global instance method implicit missing key caught"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    def get(self) -> int:
        return self.d["b"]


_g = C()


#@ ensures \result == 0
def probe() -> int:
    try:
        v = _g.get()
    except KeyError:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
