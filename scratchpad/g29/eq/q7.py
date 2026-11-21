r"""record compared with an equal copy after mutation"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x


#@ ensures \result == True
def probe() -> bool:
    a = C(1)
    b = C(2)
    b.x = 1
    return a == b


if __name__ == "__main__":
    print("CPython:", probe())
