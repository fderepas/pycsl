from typing import List, Optional
#@ no_exception \all
def f(xs: List[Optional[str]]) -> int:
    if xs:
        return len(xs[0].strip())
    return 0
