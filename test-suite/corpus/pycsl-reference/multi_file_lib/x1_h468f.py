"""Helper for corpus 7281 (route #468): heapq.heappush on the list argument."""
import heapq
from typing import List


def g(x: List[int]) -> None:
    heapq.heappush(x, 1)
