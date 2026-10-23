r"""record in list membership uses =="""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x


#@ ensures \result == True
def probe() -> bool:
    cs: List[C] = [C(1)]
    return C(1) in cs


if __name__ == "__main__":
    print("CPython:", probe())
