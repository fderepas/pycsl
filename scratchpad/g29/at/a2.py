r"""G29 A2 — auto-trust WATCH: array-returning function with an IN-LOOP return and a local list."""
from typing import List
_ = 0  # anchor


#@ requires n >= 1
#@ ensures \length(\result) == 2
#@ ensures \result[0] == 5
def mk(n: int) -> List[int]:
    out = [0, 0]
    for i in range(n):
        if i == 0:
            out[0] = 1
            return out
    return out


if __name__ == "__main__":
    print("CPython:", mk(3))
