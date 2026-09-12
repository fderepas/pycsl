"""v47 DISAGREE — ROUTE #87's NARROWING boundary. The IR carries a list literal only when it
CHANGES the answer, so an all-ZERO literal is skipped (it already lowered faithfully). The
condition is "all elements ZERO", NOT "all EQUAL": `[7, 7, 7]` got `Array.make 3 0` from the
old emitter and is still a defect. Without this driver, narrowing to "all equal" would close
route #87 for `[1,2,3]` and leave it open here. CPython returns 7."""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [7, 7, 7]


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[0]


if __name__ == "__main__":
    print(f())
