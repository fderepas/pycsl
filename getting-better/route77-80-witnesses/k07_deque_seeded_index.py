from collections import deque
#@ ensures \result == 0
def f() -> int:
    dq = deque([5, 6, 7])
    return dq[0]
if __name__ == "__main__":
    print(f())
