from typing import List
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [132]
    a: int = 1 if any(x > 131 for x in xs) else 0
    b: int = 1 if any(x > 132 for x in xs) else 0
    return a - b
