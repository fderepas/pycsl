from collections import deque
#@ ensures \result == 3
def f() -> int:
    dq = deque([1, 2, 3])
    return len(dq)
if __name__ == "__main__":
    print(f())
