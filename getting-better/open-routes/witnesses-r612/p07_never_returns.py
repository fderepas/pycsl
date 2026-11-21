from typing import Callable
#@ ensures \result == 0
#@ assigns \nothing
def g(f: Callable[[int], int], x: int) -> int:
    f(x)
    return 0
if __name__ == "__main__":
    import itertools
    def h(x):
        for _ in itertools.count():
            pass
        return 0
    print("CPython: g(h, 0) never returns (not run); partial-correctness claim only")
