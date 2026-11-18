from typing import Callable, List
#@ requires len(xs) == 1
#@ ensures \result == 1
def g(f: Callable[[int], int], xs: List[int]) -> int:
    f(0)
    return len(xs)
if __name__ == "__main__":
    ys = [0]
    r = g(lambda x: ys.append(7) or 0, ys)
    print("VIOLATION" if r != 1 else "ok", r)
