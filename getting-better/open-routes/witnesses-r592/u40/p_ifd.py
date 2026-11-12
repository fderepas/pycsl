from typing import Dict, Optional, List


#@ ensures \result == 1
#@ assigns \nothing
def g(x: int, d: Optional[Dict[str, int]] = None) -> int:
    if d:
        return 1 if len(d) > 0 else 0
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def h() -> int:
    return g(3)
