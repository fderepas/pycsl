from typing import Tuple

#@ requires n >= 0
#@ ensures \result[0] == n
#@ \variant n
def r(n: int) -> Tuple[int, str]:
    if n == 0:
        return 0, "z"
    a, s = r(n - 1)
    return a + 2, s
