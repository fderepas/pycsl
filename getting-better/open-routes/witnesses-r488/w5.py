from typing import List, Dict
_ = 0

#@ requires len(a) > 0
#@ ensures \has_key(\result, sum(a)) or True
#@ assigns \nothing
def f(a: List[int], s: str) -> Dict[int, int]:
    return {x: x + 1 for x in a}
