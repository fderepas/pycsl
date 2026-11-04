# Route #562 advice probe: ec1230 (`len([-t for x in xs])` of `t: str`) with the advice
# followed -- apply the operator to operands CPython accepts: `[-x for x in xs]`.
from typing import List


#@ no_exception \all
def f(k: int, xs: List[int], t: str) -> int:
    return len([-x for x in xs])


if __name__ == "__main__":
    print(f(0, [1, 2], "ab"))
