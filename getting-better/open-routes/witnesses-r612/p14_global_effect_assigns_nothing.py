from typing import Callable, List
#@ ensures \result == 0
#@ assigns \nothing
def g(f: Callable[[int], int], x: int) -> int:
    f(x)
    return 0
if __name__ == "__main__":
    log = []
    r = g(lambda x: log.append(x) or 0, 0)
    print("VIOLATION (assigns \\nothing, caller-visible list mutated)" if log else "ok", r, log)
