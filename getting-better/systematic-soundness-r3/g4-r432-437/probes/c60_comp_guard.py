from typing import List, Optional

#@ no_exception \all
def f(xs: List[Optional[str]]) -> int:
    n = 0
    for y in [x.strip() for x in xs if x is not None]:
        n += 1
    return n
