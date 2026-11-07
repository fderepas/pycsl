from typing import List
#@ ensures \result == 10
#@ assigns \nothing
def f() -> int:
    a: List[int] = [10, 20, 30]
    return a[-1]
if __name__ == "__main__":
    print(f())
