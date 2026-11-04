# advice probe (route #557): witness df1202 following the advice -- declare and build the container you index
from typing import Dict, List


#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    d: Dict[int, int] = {}
    d[0] = 1
    return 1
