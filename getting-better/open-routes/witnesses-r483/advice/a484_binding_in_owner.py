"""Advice probe (route #484): witness 7676 with the peer's `h.g = lambda x: 0` written in the module that
owns `g` (`y2_ha484.g` returns 0) and the peer gone. Expected: VERIFIES."""
from y2_ha484 import g


#@ ensures \result == 0
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    print("result", f(1))
