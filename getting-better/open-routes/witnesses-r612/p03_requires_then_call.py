from typing import Callable
#@ requires f(x) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def app(f: Callable[[int], int], x: int) -> int:
    return f(x)
if __name__ == "__main__":
    import itertools
    c = itertools.count()
    h = lambda x: 1 if next(c) == 0 else -1
    assert h(0) >= 0  # the caller establishes the precondition
    r = app(h, 0)
    print("VIOLATION" if r < 0 else "ok", r)
