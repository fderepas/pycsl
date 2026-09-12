from typing import List
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = [0] * -2
    return len(a)
if __name__ == "__main__":
    print(f())
