from typing import Deque
from collections import deque

#@ no_exception \all
#@ ensures \result == 1
def g(d: Deque[int]) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(deque()))
