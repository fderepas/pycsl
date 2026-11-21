from typing import Tuple
#@ ensures \result == 2
def f() -> int:
    t: Tuple[int, int] = (1, 2)
    u = t * 2
    return len(u)
if __name__ == "__main__":
    print(f())
