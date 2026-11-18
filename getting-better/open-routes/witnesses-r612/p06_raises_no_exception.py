from typing import Callable
#@ no_exception \all
#@ ensures \result == \result
#@ assigns \nothing
def g(f: Callable[[int], int], x: int) -> int:
    return f(x)
if __name__ == "__main__":
    def h(x):
        raise ValueError("boom")
    try:
        print("ok", g(h, 0))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
