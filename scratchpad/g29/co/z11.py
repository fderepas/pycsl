r"""G29 CO-Z11 — `any` over a list built by APPEND (its length is in a sidecar, not in the Why3 array)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    xs: List[int] = []
    xs.append(5)
    return 1 if any(x == 5 for x in xs) else 0


if __name__ == "__main__":
    print("CPython:", probe())
