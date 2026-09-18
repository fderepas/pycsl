r"""plain class != """
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x


#@ ensures \result == False
def probe() -> bool:
    return C(1) != C(1)


if __name__ == "__main__":
    print("CPython:", probe())
