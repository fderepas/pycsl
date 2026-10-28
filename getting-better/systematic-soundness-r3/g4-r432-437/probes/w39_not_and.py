from typing import Optional

#@ no_exception \all
def f(x: Optional[str], y: bool) -> int:
    if not (x is not None and y):
        return len(x.strip())
    return 0
