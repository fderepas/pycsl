"""v32 DISAGREE — the `treat -1 as 0` reading of a negative index. Python gives 30; this claims the 10 a model that clamped or ignored the sign would produce."""
from typing import List


#@ ensures \result == 10
#@ assigns \nothing
def f() -> int:
    a: List[int] = [10, 20, 30]
    return a[-1]


if __name__ == "__main__":
    print(f())
