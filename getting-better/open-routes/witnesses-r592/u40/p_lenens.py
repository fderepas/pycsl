from typing import Dict, Optional, List


#@ ensures \result >= 3
#@ assigns \nothing
def g(x: int, d: Optional[Dict[str, int]] = None) -> int:
    return len(d) + x


#@ ensures \result >= 3
#@ assigns \nothing
def h() -> int:
    return g(3)
