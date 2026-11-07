import heapq
from typing import List, Optional
#@ no_exception \all
def f(h: List[Optional[int]]) -> int:
    heapq.heapify(h)
    return len(h)
