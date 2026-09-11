"""v31 AGREE — a NEGATIVE list index counts from the end: `[10, 20, 30][-1]` is 30, not the first element and not an error."""
from typing import List


#@ ensures \result == 30
#@ assigns \nothing
def f() -> int:
    a: List[int] = [10, 20, 30]
    return a[-1]


if __name__ == "__main__":
    print(f())
