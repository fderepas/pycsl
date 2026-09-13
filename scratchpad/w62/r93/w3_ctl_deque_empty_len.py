from collections import deque

#@ ensures \result == 0
def f() -> int:
    dq = deque()
    return len(dq)
