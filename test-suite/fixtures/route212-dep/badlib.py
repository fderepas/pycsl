# The dependency whose own contract is FALSE of its body: `assigns \nothing` over a write
# to a list parameter. It does NOT verify standalone, which is the point.
from typing import List

_ = 0  # anchor

_state: List[int] = [0]


#@ requires n >= 0
#@ assigns \nothing
#@ ensures \result >= 0
def bump(n: int) -> int:
    _state[0] = n
    return n
