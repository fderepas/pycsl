"""Advice probe (route #483): witness 7670 with the dependency's `__builtins__['exec']` moved into a
function the program does not call at import time (`y2_ha483._later`). Expected: VERIFIES."""
from y2_ha483 import K


#@ ensures \result == n
def f(n: int) -> int:
    return n * K


if __name__ == "__main__":
    print("result", f(1))
