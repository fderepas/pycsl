# advice of PYCSL-R598-RAISE-CONSTRUCTOR-ARITY followed (rt57 hr1840 with the keyword dropped, its data bound to a local; = corpus control 9685)
# pycsl-expected: PASS
from typing import Any


#@ requires k >= 0
#@ no_exception \all
#@ ensures \result == k + 1
def f(k: int) -> int:
    q = 1
    r = 0
    try:
        raise ValueError("a")
    except ValueError:
        r = k + q
    return r


if __name__ == "__main__":
    print("result", f(4))
