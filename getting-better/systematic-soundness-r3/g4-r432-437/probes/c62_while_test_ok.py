from typing import Optional

#@ no_exception \all
def f(x: Optional[str]) -> int:
    n = 0
    if x is not None:
        while x.startswith("a"):
            n += 1
            x = x[1:]
    return n
