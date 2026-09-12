from typing import Dict
#@ ensures \result == 1
def f() -> int:
    d: Dict[int, int] = {1: 1, 2: 2}
    del d[1:2]
    return d[1]
if __name__ == "__main__":
    print(f())
