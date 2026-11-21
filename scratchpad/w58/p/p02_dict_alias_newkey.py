from typing import Dict
#@ ensures \result == 1
def f() -> int:
    a: Dict[int, int] = {1: 1}
    b: Dict[int, int] = a
    b[2] = 5
    return len(a)
if __name__ == "__main__":
    print(f())
