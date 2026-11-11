from typing import Dict, Optional, List


#@ no_exception \all
#@ assigns \nothing
def g(x: int, d: Optional[Dict[str, int]] = None) -> int:
    e = dict(d)
    return len(e) + x


#@ no_exception \all
#@ assigns \nothing
def h() -> int:
    return g(3)
