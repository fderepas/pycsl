from collections import deque

#@ ensures \result == 0
def f() -> int:
    dq = deque()
    dq.append(7)
    return len(dq)
