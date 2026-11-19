from typing import Optional
MaybeStr = Optional[str]
#@ no_exception \all
def f(x: MaybeStr) -> int:
    return len(x.strip())
