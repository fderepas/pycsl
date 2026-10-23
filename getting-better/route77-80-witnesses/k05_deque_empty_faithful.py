from collections import deque
#@ ensures \result == 0
def f() -> int:
    dq = deque()
    return len(dq)
if __name__ == "__main__":
    print(f())
