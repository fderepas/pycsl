from collections import deque

#@ no_exception \all
#@ ensures \result == 1
def g(d: deque) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(deque()))
