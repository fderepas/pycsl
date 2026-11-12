# advice of PYCSL-R597-RAISE-NAME-REBOUND followed (rt57 hs1930 with the local renamed; = corpus control 9684)
# pycsl-expected: PASS
from typing import Any


class E(Exception):
    pass


#@ requires k >= 0
#@ no_exception \all
#@ ensures \result == k + 1
def f(k: int) -> int:
    T = int
    r = 0
    try:
        raise E("a")
    except E:
        r = k + 1
    return r


if __name__ == "__main__":
    print("result", f(4))
