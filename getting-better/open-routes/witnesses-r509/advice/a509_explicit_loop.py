# advice of PYCSL-R509-COMPREHENSION-OVERFLOW-SITE applied to 8067 (`v = ["ab" * n for _ in range(1)]`): explicit loop
from typing import List


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    v: List[str] = []
    for _ in range(1):
        t = "ab" * n
        v.append(t)
    return 1


if __name__ == "__main__":
    print("result", f(5))
