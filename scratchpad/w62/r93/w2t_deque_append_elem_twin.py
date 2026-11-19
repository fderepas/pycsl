from collections import deque

#@ ensures \result == 7
def f() -> int:
    dq = deque()
    dq.append(7)
    return dq[0]
