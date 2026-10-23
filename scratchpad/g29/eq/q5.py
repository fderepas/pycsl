r"""dataclass eq=False identity"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
_ = 0  # anchor


@dataclass(eq=False)
class P:
    x: int


#@ ensures \result == True
def probe() -> bool:
    return P(1) == P(1)


if __name__ == "__main__":
    print("CPython:", probe())
