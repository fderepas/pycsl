# Route #562 advice probe: eb1241 (`len([h(t) for x in xs])` of `def h(x: int)`, `t: str`) with
# the advice followed -- pass a value of the declared kind: `[h(x) for x in xs]`.
from typing import List


def h(x: int) -> int:
    return x + 1


#@ no_exception \all
def f(k: int, xs: List[int], t: str) -> int:
    return len([h(x) for x in xs])


if __name__ == "__main__":
    print(f(0, [1, 2], "ab"))
