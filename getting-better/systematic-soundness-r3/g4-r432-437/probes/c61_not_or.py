from typing import Optional

#@ no_exception \all
def f(x: Optional[str], y: bool) -> int:
    if not (x is None or y):
        return len(x.strip())
    return 0
